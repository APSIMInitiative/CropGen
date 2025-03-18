import logging
import time

from lib.utils.job_runner import JobRunner
from lib.jobs_client.jobs_client_factory import JobsClientFactory
from lib.server.server_state import ServerState
from lib.server.job_state import JobState
from lib.utils.constants import Constants
from lib.utils.memory_usage_tracker import MemoryUsageTracker
from lib.version.software_version_info import SoftwareVersionInfo

class CropGenRunner():

    def __init__(self, config, env_provider):
        self.config = config
        self.env_provider = env_provider
        self.jobs_client = JobsClientFactory.create(config, env_provider)
        self.cgm_relay_address = self.jobs_client.retrieve_cgm_relay_address()
        self.memory_usage_tracker = MemoryUsageTracker()
        self.version_info = SoftwareVersionInfo()
        
        if not self.cgm_relay_address:
            raise Exception(f"Failed to find {Constants.CGM_RELAY_APP_NAME}")
        
        self.server_state = ServerState(config, env_provider, self.jobs_client)

        self.log_app_startup()


    def log_app_startup(self):
        logging.info("Started CropGen application")
        logging.info("Service Config: %s", self.config.to_json(self.config.PrettyPrintJsonInLogs))        
        logging.info(self.version_info.to_string())


    def poll_for_job_and_run(self):
        try:
            if (self.server_state.job_state == JobState.Running or
                self.server_state.job_state == JobState.Pending
            ):
                logging.debug("Job is currenly running")
            else:
                crop_gen_job = self.server_state.retrieve_job()

                if crop_gen_job:
                    if len(crop_gen_job.errors) == 0:
                        self.server_state.job_pending(crop_gen_job)
                        self.run_job(crop_gen_job)
                        logging.info("Finished running job. Polling for new job in '%d' seconds", self.config.SleepBetweenJobsSeconds)
                    else:
                        self.server_state.job_error(crop_gen_job.errors)

            time.sleep(self.config.SleepBetweenJobsSeconds)
        except Exception as e:
            exception_details = [str(type(e).__name__), str(e)]
            self.server_state.job_error(exception_details)
            raise


    def run_job(self, crop_gen_job):
        logging.info("Found CropGen job to run.")

        self.server_state.job_running()
        
        job_runner = JobRunner(
            self.env_provider,
            self.config, 
            self.server_state,
            self.cgm_relay_address,
            crop_gen_job,
            self.memory_usage_tracker,
            self.version_info
        )

        job_runner.run()

        self.server_state.job_finished()