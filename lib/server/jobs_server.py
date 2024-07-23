import logging

from lib.server.job_state import JobState 

class JobsServer():
    def __init__(self, jobs_client):
        self.jobs_client = jobs_client
        self.job_state = JobState.Created
        self.running_job = None


    def retrieve_job(self):
        self.running_job = self.jobs_client.retrieve_new_job()

        if not self.running_job: return None

        if self.running_job.errors and len(self.running_job.errors) > 0:
            self.log_job_errors(self.running_job.errors)
            return None
                
        self.set_job_state(JobState.Pending)

        return self.running_job
    

    def log_job_errors(self, errors):
        logging.error("CropGenJob has the following errors:")

        for error in errors:
            logging.info(error)

        logging.error("Setting job state as error.")

        self.job_error()
    

    def job_error(self):
        self.set_job_state(JobState.Error)


    def set_job_state(self, job_state):
        if self.running_job:
            test = 0
            #self.jobs_client.update_job_status(self.running_job.id, job_state)

        self.job_state = job_state