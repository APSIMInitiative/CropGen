import logging
import requests
import json
import time
from typing import Optional

from lib.models.run.crop_gen_job import CropGenJob

class JobsClient:
    def __init__(
        self, 
        client: requests.Session, 
        environment_variables_provider
    ):
        self._client = client
        self._hpc_id = environment_variables_provider.get_hpc_id()
        base_url = environment_variables_provider.get_jobs_server_address()
        self._client.base_url = base_url

        logging.info(f"HPC ID: {self._hpc_id}")
        logging.info(f"Base URL: {base_url}")


    def retrieve_service(self, name: str):
        url = f"{self._client.base_url}/api/services/address/{name}/{self._hpc_id}"
        retries = 5

        while retries > 0:
            response = self._client.get(url)
            if response.status_code == 200:
                address = response.text
                if address:
                    logging.info(f"Server query for: {name}. Response: {address}")
                    return address
                retries -= 1
                time.sleep((6 - retries) * 1)
                logging.warning(f"{name} not registered ({retries} attempts remaining)")
        
        return None
    

    def retrieve_new_job(self):
        url = f"{self._client.base_url}/api/queue/nextjob/{self._hpc_id}/cropgen"
        job = self._retrieve_data_from_json(url)
        if job:
            crop_gen_job = CropGenJob()
            crop_gen_job.parse_from_json_string(job)
            return crop_gen_job
        return None


    def update_job_status(
        self, 
        id: str, 
        status: str, 
        current_iteration: Optional[int] = None,
        total_iterations: Optional[int] = None, 
        avg_run_time: Optional[float] = None
    ):
        url = f"{self._client.base_url}/api/queue/status/{id}"
        update_job_status_request = {
            "Id": id,
            "Status": status,
            "CurrentIteration": current_iteration,
            "TotalIterations": total_iterations,
            "AvgRunTime": avg_run_time
        }
        json_data = json.dumps(update_job_status_request)
        response = self._client.put(url, data=json_data, headers={"Content-Type": "application/json"})

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Invalid response when updating status")


    def _retrieve_data_from_json(self, url: str):
        response = self._client.get(url)
        if response.status_code == 200:
            return response.json()
        return None