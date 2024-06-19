# Imports
import logging
import requests
import time

from lib.logging.logger_config import LoggerConfig
from lib.config.crop_gen_config import CropGenConfig
from lib.utils.environment_variables_provider import EnvironmentVariablesProvider
from lib.utils.job_runner import JobRunner
from lib.utils.jobs_client import JobsClient
from lib.server.server_state import ServerState
from lib.server.job_state import JobState
from lib.utils.constants import Constants
from lib.socket.zmq_client import ZMQClient

class CropGenRunner():

    def __init__(self):
        self.config = CropGenConfig()
        self.config._parse()

        self.logger_config = LoggerConfig(self.config)
        self.logger_config.setup_logger(True)

        self.env_provider = EnvironmentVariablesProvider()
        self.http_client = requests.Session()
        self.jobs_client = JobsClient(self.http_client, self.env_provider)
        self.job_runner = JobRunner(self.config)
        self.server_state = ServerState(self.jobs_client)

        self.cgm_relay_address = self.jobs_client.retrieve_service(Constants.CGM_RELAY_APP_NAME)
        if not self.cgm_relay_address:
            raise Exception(f"Failed to find {Constants.CGM_RELAY_APP_NAME}")
        
        self.zmq_client = ZMQClient(self.config)


    def log_app_startup(self):
        logging.info("Started CropGen application")
        logging.info("Service Config: %s", self.config.to_json(self.config.PrettyPrintJsonInLogs))


    def run(self):
        if self.server_state.job_state == JobState.Running or self.server_state.job_state == JobState.Pending:
            logging.debug("Job is currenly running.")
        else:
            job = self.server_state.retrieve_job()
            if job:
                logging.info("Found CropGen job to run.")
                self.job_runner.run(job)

        time.sleep(60000)
