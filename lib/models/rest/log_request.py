from lib.models.common.model import Model

#
# A log message that is sent to a remote server.
#
class LogRequest(Model):
    #
    # Constructor
    #
    def __init__(
        self,
        record
    ):
        self.Filename =  record.filename
        self.Timestamp = record.asctime
        #self.Timestamp = record.timestamp
        self.LogLevel = record.levelname
        self.Message = record.message
    
    #
    # Returns the type name.
    #
    def get_type_name(self):
        return __class__.__name__