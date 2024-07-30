import logging
import json
import os

from lib.models.common.model import Model
from lib.utils.constants import Constants

#
# The config for this application.
#
class Config(Model):
    # The environment variable that is created only when running in a container.
    RUNNING_IN_CONTAINER = 'RUNNING_IN_CONTAINER'
    CONFIG_FILE_FULL_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
    OVERRIDE_CONFIG_FILE_FULL_PATH = os.path.join(os.path.dirname(__file__), 'config_override.json')
    IS_RUNNING_IN_DOCKER = os.environ.get(RUNNING_IN_CONTAINER, False)

    #
    # Constructor.
    #
    def __init__(self, env_provider) -> None:
        super().__init__()
        self.env_provider = env_provider
        self.cropgen_runtime_dir = self.create_runtime_dir()
        self.log_dir = os.path.join(self.cropgen_runtime_dir, "logs")
        self.results_dir = os.path.join(self.cropgen_runtime_dir, "results")
        self.jobs_dir = os.path.join(self.cropgen_runtime_dir, "jobs")

        self.create_run_time_subdirs()

    #
    # Creates a runtime directory for CropGen to use.
    #
    def create_runtime_dir(self):
        runtime_dir = self.env_provider.get_hpc_root_dir()
        if not runtime_dir:
            this_script_path = os.path.dirname(os.path.abspath(__file__))
            runtime_dir = os.path.join(this_script_path, "..", "..", "runtime")

        runtime_dir = os.path.join(runtime_dir, Constants.APPLICATION_NAME.lower())
        runtime_dir = os.path.abspath(runtime_dir)

        os.makedirs(runtime_dir, exist_ok=True)

        return runtime_dir
    
    #
    # Create all of the other run time dirs.
    #
    def create_run_time_subdirs(self):
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.jobs_dir, exist_ok=True)

    #
    # Parses the config JSON file and stores it in memory.
    #
    def _parse(self):
        config_file_to_use = Config.CONFIG_FILE_FULL_PATH

        if os.path.exists(Config.OVERRIDE_CONFIG_FILE_FULL_PATH):
            logging.warn("Found an override config: %s. This will be used to configure CropGen.", Config.OVERRIDE_CONFIG_FILE_FULL_PATH)
            config_file_to_use = Config.OVERRIDE_CONFIG_FILE_FULL_PATH

        with open(config_file_to_use) as json_config_file:
            data = json.load(json_config_file)

        self._populate_from_data(data)
    
    #
    # Populates itself using the config JSON data.
    #
    def _populate_from_data(self, data):
        self.SocketServerHost = self._get_config_setting(data, 'SocketServerHost', 'localhost')
        self.SocketServerPort = self._get_config_setting(data, 'SocketServerPort', 8000)
        self.SocketDataNumBytesBufferSize = self._get_config_setting(data, 'SocketDataNumBytesBufferSize', 4)
        self.SocketDataEndianness = self._get_config_setting(data, 'SocketDataEndianness', 'big')        
        self.SocketDataEncoding = self._get_config_setting(data, 'SocketDataEncoding', 'utf-8')
        self.SocketTimeoutSeconds = self._get_config_setting(data, 'SocketTimeoutSeconds', 0.0)
        self.SocketTimeoutTestConnectionSeconds = self._get_config_setting(data, 'SocketTimeoutTestConnectionSeconds', 2.0)
        self.MaxSocketReceiveSize = self._get_config_setting(data, 'MaxSocketReceiveSize', 0)        
        self.ResultsPublisherTimeoutSeconds = self._get_config_setting(data, 'ResultsPublisherTimeoutSeconds', 30)
        self.PublishResults = self._get_config_setting(data, 'PublishResults', True)
        self.PrettyPrintJsonInLogs = self._get_config_setting(data, 'PrettyPrintJsonInLogs', False)        
        self.DeleteLogsOnStartup = self._get_config_setting(data, 'DeleteLogsOnStartup', False)
        self.RoundUpYearsInMeanCalculation = self._get_config_setting(data, 'RoundUpYearsInMeanCalculation', False)
        self.MinimumRequiredCGMWorkers = self._get_config_setting(data, 'MinimumRequiredCGMWorkers', 1)
        self.ApsimClockStartDateYearInputName = self._get_config_setting(data, 'ApsimClockStartDateYearInputName', 'Clock.StartDate')
        self.ApsimClockEndDateYearInputName = self._get_config_setting(data, 'ApsimClockEndDateYearInputName', 'Clock.EndDate')
        self.ApsimSimulationStartDate = self._get_config_setting(data, 'ApsimSimulationStartDate', '1900-06-01')
        self.ApsimClockDateFormat = self._get_config_setting(data, 'ApsimClockDateFormat', "%m/%d/%Y")
        self.ApsimSimulationStartDateAddYear = self._get_config_setting(data, 'ApsimSimulationStartDateAddYear', 0)
        self.ApsimSimulationEndDateAddYear = self._get_config_setting(data, 'ApsimSimulationEndDateAddYear', 0)
        self.ConsoleLogLevel = self._get_config_setting(data, 'ConsoleLogLevel', "INFO")
        self.FileLogLevel = self._get_config_setting(data, 'FileLogLevel', "DEBUG")
        self.RemoteLogLevel = self._get_config_setting(data, 'RemoteLogLevel', "INFO")
        self.RemoteLoggerUrl = self._get_config_setting(data, 'RemoteLoggerUrl', '')
        self.RestartAfterConfigUpdate = self._get_config_setting(data, 'RestartAfterConfigUpdate', False)
        self.InitWorkersPreRunSimulations = self._get_config_setting(data, 'InitWorkersPreRunSimulations', False)
        self.AlwaysResetRunner = self._get_config_setting(data, 'AlwaysResetRunner', False)
        self.SleepBetweenJobsSeconds = self._get_config_setting(data, 'SleepBetweenJobsSeconds', 60)

    #
    # Writes this config, back to disk.
    #
    def write_to_disk(self):
        try:
            with open(Config.OVERRIDE_CONFIG_FILE_FULL_PATH, 'w') as json_config_file:
                json_config_file.write(self.to_json(True))
        except Exception:
            logging.exception("Error while writing config to disk.")
            return False

        return True

    #
    # Safely gets a config setting, taking into consideration container
    # and defaults if it isn't present.
    #
    def _get_config_setting(
        self,
        data,
        config_key,
        default_if_not_present = None
    ):
        # Any config value can be overriden by simply appending the word Docker 
        # to the end of the key in the config json file. Construct a container key
        # so that we can check for the presence of this.
        container_override_config_key = f"{config_key}Container"

        # Check for a Docker config override key.
        if self._get_config_exists(data, container_override_config_key) and Config.IS_RUNNING_IN_DOCKER:
            return self._get_config_value(data, container_override_config_key, default_if_not_present)

        return self._get_config_value(data, config_key, default_if_not_present)
    
    #
    # Safely extracts the value using the key, or defaults if it's not present.
    #
    def _get_config_value(
        self,
        data,
        config_key, 
        default_if_not_present = None
    ):
        value = default_if_not_present
        if self._get_config_exists(data, config_key):
            value = data[config_key]
        return value

    #
    # Checks if the config key exists
    #
    def _get_config_exists(self, data, config_key):
        return config_key in data
    
    #
    # Returns the type name.
    #
    def get_type_name(self):
        return __class__.__name__
