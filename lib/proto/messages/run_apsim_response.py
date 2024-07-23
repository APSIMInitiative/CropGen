import lib.proto.path.proto_paths
import RunApsimResponse_pb2
import ApsimResult_pb2

from lib.proto.base.proto_response import ProtoResponse
from lib.proto.messages.apsim_result import ApsimResult

class RunApsimResponse(ProtoResponse):
    def __init__(self):
        self.id = ''
        self.jobId = ''
        self.fields = []
        self.rows = []
        self.runTime = 0.0
        self.runSource = ''


    @staticmethod
    def from_proto(proto):
        run_apsim_response = RunApsimResponse()
        run_apsim_response.id = proto.ID
        run_apsim_response.jobId = proto.JobID
        run_apsim_response.fields = list(proto.Fields)
        run_apsim_response.rows = [ApsimResult.from_proto(row) for row in proto.Rows]
        
        if proto.HasField('RunTime'):
            run_apsim_response.runTime = proto.RunTime

        if proto.HasField('RunSource'):
            run_apsim_response.runSource = proto.RunSource

        return run_apsim_response
    

    def get_apsim_results_for_individual(self, individual):
        apsim_results = []
        for row in self.rows:
            if row.id == individual:
              apsim_results.append(row)
        return apsim_results
    

    @staticmethod
    def get_proto_type() -> type:
        return RunApsimResponse_pb2.RunApsimResponseProto
    

    def get_type_name(self):
        return __class__.__name__ + "Proto"