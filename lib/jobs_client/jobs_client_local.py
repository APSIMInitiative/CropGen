import time
import os
import logging
from typing import Optional

from lib.server.job_state import JobState
from lib.jobs_client.job_manager import JobFileManager

class JobsClientLocal:
    
    def __init__(
        self,
        config,
        environment_variables_provider
    ):
        self.config = config
        self.job_file_manager = JobFileManager(config)
        self._hpc_id = environment_variables_provider.get_hpc_id()
        self.relay_ip_file = environment_variables_provider.get_relay_ip_file()
        self.relay_ip_address = ""

        logging.info(f"HPC ID: {self._hpc_id}")
        logging.info(f"RELAY IP FILE: {self.relay_ip_file}")

        self.parse_relay_ip_address_file()


    def parse_relay_ip_address_file(self):
        self.wait_for_file_or_throw()

        try:
            with open(self.relay_ip_file, 'r') as file:
                file_contents = file.read()
                if file_contents:
                    self.relay_ip_address = file_contents.strip()
        except Exception as ex:
            logging.error("Error reading Relay IP file: %s. Exception: %s", self.relay_ip_file, ex)
            raise


    def wait_for_file_or_throw(self):
        max_attempts = 30
        sleep_time_seconds = 1
        file_exists = False
        attempt = 0

        while not file_exists and attempt < max_attempts:
            file_exists = os.path.exists(self.relay_ip_file)

            if file_exists:
                break

            time.sleep(sleep_time_seconds)
            sleep_time_seconds *= 2
            attempt += 1

        if not file_exists:
            raise FileNotFoundError(f"Failed to find relay IP file after {max_attempts} attempts.")        


    def retrieve_cgm_relay_address(self):
        return self.relay_ip_address
    

    def retrieve_new_job(self):
        self.job_file_manager.retrieve_new_job()


    def update_job_status(
        self, 
        id: str, 
        status: JobState, 
        current_iteration: Optional[int] = 0,
        total_iterations: Optional[int] = 0, 
        avg_run_time: Optional[float] = 0
    ):
        pass