import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'autogen')))

import ApsimConfig_pb2
import InitApsim_pb2

class InitApsim():

    def __init__(self, config):
        self.config = config

    def to_proto(self, crop_gen_job):
        
        init_proto = InitApsim_pb2.InitApsimProto()
        init_proto.JobID = crop_gen_job.jobId
        init_proto.Url = ""
        init_proto.PreRunSimulations = False
        init_proto.ResetRunner = self.config.AlwaysResetRunner
        init_proto.Configuration = ApsimConfig_pb2.ApsimConfigProto()

        apsim_config_proto = ApsimConfig_pb2.ApsimConfigProto()
        
        return init_proto
