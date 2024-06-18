#
# Main application entry point.
#

# Imports
import logging
import requests

from lib.logging.logger_config import LoggerConfig
from lib.config.crop_gen_config import CropGenConfig
from lib.utils.environment_variables_provider import EnvironmentVariablesProvider
from lib.utils.job_runner import JobRunner
from lib.utils.jobs_client import JobsClient
from lib.server.server_state import ServerState
from lib.server.job_state import JobState

config = CropGenConfig()
config._parse()
server_state = ServerState()

def log_app_startup():
    logging.info("Started CropGen application")
    logging.info("Service Config: %s", config.to_json(config.PrettyPrintJsonInLogs))
    

# Main entry point
if __name__ == "__main__":

    try:
        logger_config = LoggerConfig(config)
        logger_config.setup_logger(True)

        env_provider = EnvironmentVariablesProvider()
        http_client = requests.Session()
        jobs_client = JobsClient(http_client, env_provider)
        job_runner = JobRunner(config)

        log_app_startup()

        cgm_relay_address = jobs_client.retrieve_service("CGMRelay")
        if not cgm_relay_address:
            raise Exception("Failed to find CGMRelay")

        # Run the loop forever until a keyboard event occurs
        while True:
            try:
                
                if server_state.job_state == JobState.Running or server_state.job_state == JobState.Pending:
                    logging.debug("Job is currenly running, wait a minute before checking again.")
                else:
                    # Poll for a job
                    crop_gen_job = jobs_client.retrieve_new_job()

                    if crop_gen_job:
                        jobs_client.update_job_status(crop_gen_job.jo)
                        job_runner.run(crop_gen_job)

            except KeyboardInterrupt: 
                # Break out of the loop on a keyboard event
                logging.info("Keyboard interrupt. Exiting...")
                break

        logging.info("Closing CropGen application")
    except:
        logging.exception("Exception - CropGen Main Application catch handler")
