from lib.models.model import Model
from lib.utils.date_time_helper import DateTimeHelper

#
# An error message containing a list of errors and a date time.
#
class ErrorMessage(Model):
    #
    # Constructor, requires the errors.
    #
    def __init__(self, errors):
        self.message_type = __class__.__name__
        self.date_time = DateTimeHelper.get_date_time_now_str()
        self.errors = errors

    #
    # Returns the type name.
    #
    def get_type_name(self):
        return __class__.__name__