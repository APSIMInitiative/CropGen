import glob
import logging
import logging.handlers
import logging.config
import os.path
import requests

from http import HTTPStatus
from lib.models.rest.log_request import LogRequest

class LoggerConfig:

    #
    # Constructor.
    #
    def __init__(self, config, env_provider):
        self.config = config
        self.env_provider = env_provider
        self.this_script_path = os.path.dirname(__file__)
        self.log_directory = self.get_log_dir()
        self.log_file = os.path.join(self.log_directory, 'cropgen.log')

    def get_log_dir(self):
        hpc_root_dir = self.env_provider.get_hpc_root_dir()
        if hpc_root_dir:
            return os.path.join(hpc_root_dir, "cropgen_logs")

        return os.path.join(self.this_script_path, "..", "..", "logs")

    #
    # Configures the logger.
    #
    def setup_logger(self, is_starting_up=False):
        if is_starting_up and self.config.DeleteLogsOnStartup:
            self._delete_all_log_files()
            
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        # Add the HTTPS handler
        self.remove_all_log_handlers()
        self.add_remote_logger()
        self.set_log_levels()
        self.set_third_party_log_levels()

    #
    # Removes all of the log handlers before adding new ones.
    #
    def remove_all_log_handlers(self):
        root_logger = logging.getLogger()

        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    #
    # Sets up the log levels used by this application.
    #
    def set_log_levels(self):

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] - %(name)s - %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S %Z%z'
        )

        # Console handler
        console_level = LoggerConfig.string_to_logging_level(self.config.ConsoleLogLevel)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

         # File handler
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            # 10 MB
            maxBytes=10485760,
            backupCount=2
        )

        # Set file logging level
        file_level = LoggerConfig.string_to_logging_level(self.config.FileLogLevel)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    #
    # Sets the log levels for our third party libraries.
    #
    def set_third_party_log_levels(self):
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger('asyncio'). setLevel(logging. WARNING) 

    #
    # Cleans up any existing .log files.
    #
    def _delete_all_log_files(self):
        if os.path.exists(self.log_directory):
            log_files = glob.glob(f'{self.log_directory}/*.log*')
            for file in log_files:
                os.remove(file)

    #
    # Adds a remote logger.
    #    
    def add_remote_logger(self):
        if not self.config.RemoteLoggerUrl:
            return

        # Use the custom handler
        handler = CustomHttpsHandler(self.config)

        # Add the handler to the root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

    #
    # A simple helper for converting a human readable log level string
    # into a log level that is used by the logging framework.
    #
    @staticmethod
    def string_to_logging_level(level_str):
        level_mapping = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "information": logging.INFO,
            "warn": logging.WARNING,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }
        
        trimmed_level_str = level_str.strip().lower()
        level = logging.INFO
        
        if trimmed_level_str in level_mapping: 
            level = level_mapping[trimmed_level_str]

        return level


#
# A custom handler.
#
class CustomHttpsHandler(logging.Handler):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.session = requests.Session()
        self.stop_sending_logs_to_server = False

        self.setLevel(LoggerConfig.string_to_logging_level(self.config.RemoteLogLevel))

    def emit(self, record):
        if self.stop_sending_logs_to_server:
            return
            
        try:
            log_request = LogRequest(record)

            response = requests.put(
                headers={'Content-type': 'application/json'},
                url=self.config.RemoteLoggerUrl, 
                data=log_request.to_json()
            )

            if response.status_code != HTTPStatus.OK:
                error = f"Failed to send logs to the server: '{self.url}'. HTTP Status Code: {response.status_code}"
                raise Exception(error)
        except Exception as ex:
            # Log the error and stop retrying
            print(f"Error sending logs: {ex}")
            self.stop_sending_logs_to_server = True