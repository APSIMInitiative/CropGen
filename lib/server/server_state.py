from lib.server.job_state import JobState 

class ServerState():
    def __init__(self, jobs_client):
        self.jobs_client = jobs_client
        self.job_state = JobState.Created

    def retrieve_job(self):
        crop_gen_job = self.jobs_client.retrieve_new_job()

        if crop_gen_job:
            self.jobs_client.update_job_status(crop_gen_job.id, JobState.Pending)
            self.job_state = JobState.Pending
            return crop_gen_job
        return None