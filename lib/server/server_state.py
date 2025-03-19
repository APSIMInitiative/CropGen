import logging
import os

from lib.server.job_state import JobState 

class ServerState():
    def __init__(self, config, env_provider, jobs_client):
        self.config = config
        self.jobs_client = jobs_client
        self.update_frequency = env_provider.get_update_freq()
        self.job_state = JobState.Created
        self.running_crop_gen_job = None

    def retrieve_job(self):
        crop_gen_job = self.jobs_client.retrieve_new_job()

        if not crop_gen_job: return None

        if crop_gen_job.errors:
            self.job_error(crop_gen_job.errors)
            return None

        return crop_gen_job


    def job_pending(self, crop_gen_job):
        self._set_job_state(JobState.Pending)
        self.running_crop_gen_job = crop_gen_job


    def job_running(self):
        self._set_job_state(JobState.Running)
        self._create_job_started_file()


    def _create_job_started_file(self):
        self._remove_job_started_file()

        with open(self.config.job_running_filename, 'a') as file:
            file.write(self.running_crop_gen_job.to_json(True))

    
    def _remove_job_started_file(self):
        if os.path.exists(self.config.job_running_filename):
            os.remove(self.config.job_running_filename)


    def job_finished(self):
        self._set_job_state(JobState.Finished)
        self._clear_running_job()


    def job_error(self, errors):
        logging.error("CropGenJob has the following errors:")
        for error in errors: logging.info(error)
        logging.error("Setting job state as error.")
        
        self._set_job_state(JobState.Error)

        id = self.running_crop_gen_job.id if self.running_crop_gen_job else None
            
        self.jobs_client.job_error(id, errors)
        self._clear_running_job()


    def _clear_running_job(self):
        self.running_crop_gen_job = None
        self._remove_job_started_file()


    def _set_job_state(self, job_state):
        self.job_state = job_state        
        if self.running_crop_gen_job:
            self.jobs_client.update_job_status(self.running_crop_gen_job.id, job_state)


    def set_iteration_complete(self, iteration, avg_run_time):
        if self.running_crop_gen_job:
            if self.should_update_progress(iteration, self.running_crop_gen_job.iterations):
                self.jobs_client.update_job_status(
                    self.running_crop_gen_job.id,
                    JobState.Running,
                    iteration,
                    self.running_crop_gen_job.iterations,
                    avg_run_time
                )

    
    def should_update_progress(self, current_iteration, total_iterations):
        # If the update frequency is set to 1, or if it should report at this iteration
        if self.update_frequency == 1:
            return True
        
        # Determine if it is time to report based on the current/total iterations
        return (
            current_iteration <= 5 or
            current_iteration >= total_iterations or
            current_iteration % self.update_frequency == 0
        )


    def set_job_complete(self):
        self.jobs_client.job_complete()