from lib.models.model import Model
from lib.utils.date_time_helper import DateTimeHelper

class Data:
    def __init__(self, job_id, duration_seconds):
        self.job_id = job_id        
        self.date_time = DateTimeHelper._get_date_time_now_str()
        self.duration_seconds = duration_seconds

class EndOfRunMessage(Model):
    def __init__(self, job_type, job_id, duration_seconds):
        self.message_type = __class__.__name__
        self.job_type = job_type
        self.data = Data(job_id, duration_seconds)