import lib.proto.path.proto_paths
import InitApsimResponse_pb2

from lib.proto.base.proto_response import ProtoResponse

class InitApsimResponse(ProtoResponse):

    def __init__(self):
        self.id = ''
        self.jobId = ''
        self.firstRunTime = 0.0
        self.secondRunTime = 0.0
        self.runSource = ''


    @staticmethod
    def from_proto(proto):
        init_apsim_response = InitApsimResponse()
        init_apsim_response.id = proto.ID
        init_apsim_response.jobId = proto.JobID
        if proto.HasField('FirstRunTime'):
            init_apsim_response.firstRunTime = proto.FirstRunTime
        if proto.HasField('SecondRunTime'):
            init_apsim_response.secondRunTime = proto.SecondRunTime
        if proto.HasField('RunSource'):
            init_apsim_response.runSource = proto.RunSource
        return init_apsim_response
    

    @staticmethod
    def get_proto_type() -> type:
        return InitApsimResponse_pb2.InitApsimResponseProto
    

    @staticmethod
    def get_type_name():
        return __class__.__name__ + "Proto"