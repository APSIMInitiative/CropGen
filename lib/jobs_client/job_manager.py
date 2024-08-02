import logging
import os
import glob
import json

from lib.models.run.crop_gen_job import CropGenJob
from lib.utils.date_time_helper import DateTimeHelper

class JobFileManager:

    JOB_FILE_EXT = "json"
    LOCK_FILE_EXT = "lock"
    ERROR_FILE_EXT = "error"

    def __init__(self, config):
        self.config = config
        self.job_file = ""
        self.lock_file = ""

    def _get_job_files(self):
        job_files = glob.glob(os.path.join(self.config.jobs_dir, f'*.{JobFileManager.JOB_FILE_EXT}'))
        valid_job_files = []

        for job_file in job_files:
            ignore_paths = self.get_ignore_jobs_for_job_file(job_file)

            if not any(os.path.exists(path) for path in ignore_paths):
                valid_job_files.append(job_file)

        return valid_job_files
    


    def get_ignore_jobs_for_job_file(self, job_file):
        return [
            self._get_lock_file_path(job_file),
            self._get_error_file_path(job_file)
        ]
    

    def _get_lock_file_path(self, job_file):
        return job_file.replace(f'.{JobFileManager.JOB_FILE_EXT}', f'.{JobFileManager.LOCK_FILE_EXT}')
    

    def _get_error_file_path(self, job_file):
        return job_file.replace(f'.{JobFileManager.JOB_FILE_EXT}', f'.{JobFileManager.ERROR_FILE_EXT}')
    

    def retrieve_new_job(self):
        self.job_file = ""
        self.lock_file = ""
        valid_job_files = self._get_job_files()
        valid_job_files.sort(key=lambda x: os.path.getmtime(x))

        if valid_job_files:
            latest_job_file = valid_job_files[0]
            try:
                with open(latest_job_file, 'r') as file:
                    job_content = file.read()

                crop_gen_job = CropGenJob()
                crop_gen_job.parse_from_json_object(json.loads(job_content))
                self._create_lock_file(latest_job_file)
                return crop_gen_job

            except Exception as ex:
                logging.error(f"Error reading or parsing job file {latest_job_file}: {ex}")
                return None

        return None
    

    def _create_lock_file(self, job_file):
        self.job_file = job_file
        self.lock_file = self._get_lock_file_path(job_file)
        with open(self.lock_file, 'w') as file:
            file.write(f"{DateTimeHelper.get_date_time_now_str()} - Job started for: {job_file}\n")


    def append_to_lock_file(self, message):
        if os.path.exists(self.lock_file):
            with open(self.lock_file, 'a') as file:
                file.write(f"{DateTimeHelper.get_date_time_now_str()} - {message} \n")


    def rename_lock_to_error(self):
        if os.path.exists(self.lock_file):
            error_file = self.lock_file.replace(f'.{JobFileManager.LOCK_FILE_EXT}', f'.{JobFileManager.ERROR_FILE_EXT}')
            os.rename(self.lock_file, error_file)
            self.lock_file = error_file


