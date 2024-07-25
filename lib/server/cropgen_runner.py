# Imports
import logging
import requests
import time

from lib.utils.job_runner import JobRunner
from lib.utils.jobs_client import JobsClient
from lib.server.jobs_server import JobsServer
from lib.server.job_state import JobState
from lib.utils.constants import Constants

class CropGenRunner():

    def __init__(self, config, env_provider):
        self.config = config
        self.env_provider = env_provider
        self.http_client = requests.Session()
        self.jobs_client = JobsClient(self.http_client, self.env_provider)
        self.cgm_relay_address = self.jobs_client.retrieve_service(Constants.CGM_RELAY_APP_NAME)
        
        if not self.cgm_relay_address:
            raise Exception(f"Failed to find {Constants.CGM_RELAY_APP_NAME}")
        
        self.server_state = JobsServer(self.jobs_client)


    def log_app_startup(self):
        logging.info("Started CropGen application")
        logging.info("Service Config: %s", self.config.to_json(self.config.PrettyPrintJsonInLogs))


    def poll_for_job_and_run(self):
        try:
            if (self.server_state.job_state == JobState.Running or
                self.server_state.job_state == JobState.Pending
            ):
                  logging.debug("Job is currenly running.")
            else:
                crop_gen_job = self.server_state.retrieve_job()

                if crop_gen_job and len(crop_gen_job.errors) == 0:
                    self.server_state.job_pending(crop_gen_job)
                    self.run_job(crop_gen_job)

            time.sleep(self.config.SleepBetweenJobsMs)
        except:
            self.server_state.job_error()
            raise


    def run_job(self, crop_gen_job):
        logging.info("Found CropGen job to run.")

        self.server_state.job_running()
        
        job_runner = JobRunner(
            self.config, 
            self.cgm_relay_address,
            crop_gen_job
        )

        job_runner.run()

        self.server_state.job_finished(JobState.Finished)