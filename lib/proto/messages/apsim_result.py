from lib.proto.base.proto_response import ProtoResponse

class ApsimResult(ProtoResponse):
    def __init__(self):
        self.id = 0
        self.simulationID = ''
        self.simulationName = ''
        self.values = []


    @staticmethod
    def from_proto(proto):
        apsim_result = ApsimResult()
        apsim_result.id = proto.ID
        apsim_result.simulationID = proto.SimulationID
        apsim_result.simulationName = proto.SimulationName
        apsim_result.values = list(proto.Values)
        return apsim_result
            

    @staticmethod
    def get_type_name():
        return __class__.__name__