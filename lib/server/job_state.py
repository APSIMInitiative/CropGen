from enum import Enum

class JobState(Enum):
    
    # The job has been created but is not yet queued to be run.
    Created = 1

    # The job has been submitted and is in the queue to be run.
    Queued = 2

    # The job is in a pending state and will soon be run.
    Pending = 3

    # The job is currently running.
    Running = 4

    # The job has completed successfully.
    Finished = 5

    # The job completed with errors.
    Error = 6

    # The job was aborted by the user.
    Aborted = 7
