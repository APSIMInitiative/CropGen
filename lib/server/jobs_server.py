import logging

from lib.server.job_state import JobState 

class JobsServer():
    def __init__(self, jobs_client):
        self.jobs_client = jobs_client
        self.job_state = JobState.Created
        self.running_crop_gen_job = None

    def retrieve_job(self):
        crop_gen_job = self.jobs_client.retrieve_new_job()

        if not crop_gen_job: return None

        if crop_gen_job.errors:
            self._log_job_errors(crop_gen_job.errors)
            return None

        return crop_gen_job
    

    def _log_job_errors(self, errors):
        logging.error("CropGenJob has the following errors:")
        for error in errors: logging.info(error)
        logging.error("Setting job state as error.")

        self.job_error()


    def job_pending(self, crop_gen_job):
        self._set_job_state(JobState.Pending)
        self.running_crop_gen_job = crop_gen_job


    def job_running(self):
        self._set_job_state(JobState.Running)


    def job_finished(self):
        self._set_job_state(JobState.Finished)
        self._clear_running_job()


    def job_error(self):        
        self._set_job_state(JobState.Error)
        self._clear_running_job()


    def _clear_running_job(self):
        self.running_crop_gen_job = None

    def _set_job_state(self, job_state):
        if self.running_crop_gen_job:
            todo_update_state = False
            if todo_update_state:
                self.jobs_client.update_job_status(self.running_crop_gen_job.id, job_state)

        self.job_state = job_state