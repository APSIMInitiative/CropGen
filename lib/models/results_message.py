from lib.models.model import Model
from lib.utils.date_time_helper import DateTimeHelper

class Data:
    def __init__(self, job_id, data_frame):
        self.job_id = job_id
        self.date_time = DateTimeHelper._get_date_time_now_str()
        self.data = data_frame.to_json(indent=2)

class ResultsMessage(Model):
    def __init__(self, job_type, job_id, data_frame):
        self.message_type = __class__.__name__
        self.job_type = job_type
        self.data = Data(job_id, data_frame)