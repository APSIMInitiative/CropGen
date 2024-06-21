import lib.proto.proto_paths
import ApsimConfig_pb2
import InitApsim_pb2

class InitApsim():

    def __init__(self, config):
        self.config = config

    def to_proto(self, crop_gen_job):
        
        init_proto = InitApsim_pb2.InitApsimProto()
        init_proto.JobID = crop_gen_job.apsimJobId
        init_proto.Url = ""
        init_proto.PreRunSimulations = self.config.InitWorkersPreRunSimulations
        init_proto.ResetRunner = self.config.AlwaysResetRunner
        apsim_config_proto = ApsimConfig_pb2.ApsimConfigProto()
        
        for input in crop_gen_job.inputs:            
            apsim_config_proto.Inputs.append(input.Name)

        report_config_proto = apsim_config_proto.ReportDetails.add()
        report_config_proto.ReportName = crop_gen_job.reportName

        for output in crop_gen_job.outputs:
            report_config_proto.Fields.append(output.ApsimOutputName)

        init_proto.Configuration.CopyFrom(apsim_config_proto)

        return init_proto
    
    
    def get_type_name(self):
        return __class__.__name__ + "Proto"
