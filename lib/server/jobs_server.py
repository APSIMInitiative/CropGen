from lib.server.job_state import JobState 

class JobsServer():
    def __init__(self, jobs_client):
        self.jobs_client = jobs_client
        self.job_state = JobState.Created
        self.running_job = None


    def retrieve_job(self):
        crop_gen_job = self.jobs_client.retrieve_new_job()

        if crop_gen_job:
            self.running_job = crop_gen_job
            self.set_job_state(JobState.Pending)

        return crop_gen_job
    

    def job_error(self):
        self.set_job_state(JobState.Error)


    def set_job_state(self, job_state):
        if self.running_job:
            # TODO Put me back
            #self.jobs_client.update_job_status(self.running_job.id, job_state)
            self.job_state = job_state