import threading
import logging
from lib.server.job_state import JobState 

#
# Records the state of the server.
#
class ServerState():

    #
    # Constructor
    #
    def __init__(self):
        self.lock = threading.Lock()
        self.running_job = ''
        self.job_state = JobState.Created

    #
    # Get whether a job is currently running.
    #
    def get_is_job_currently_running(self):
        with self.lock:
            return self.running_job != ''

    #
    # Get the JobID of the running job.
    #
    def get_running_job_id(self):
        with self.lock:
            return self.running_job

    #
    # Set the running job.
    #
    def set_running_job_id(self, job_id):
        logging.info("Setting running job: '%s'", job_id)
        with self.lock:
            self.running_job = job_id

    #
    # Clears the running job.
    #
    def clear_running_job_id(self):
        logging.info("Clearing the current running job: '%s'", self.running_job)
        with self.lock:
            self.running_job = ''
