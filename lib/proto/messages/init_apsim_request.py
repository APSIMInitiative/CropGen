import lib.proto.path.proto_paths
import ApsimConfig_pb2
import InitApsim_pb2

from lib.proto.base.proto_request import ProtoRequest
from lib.proto.messages.init_apsim_response import InitApsimResponse

class InitApsimRequest(ProtoRequest):

    def __init__(self, config, crop_gen_job):
        self.config = config
        self.crop_gen_job = crop_gen_job

    def to_proto(self):
        init_proto = InitApsim_pb2.InitApsimProto()
        init_proto.JobID = self.crop_gen_job.apsimJobId
        init_proto.Url = ""
        init_proto.PreRunSimulations = self.config.InitWorkersPreRunSimulations
        init_proto.ResetRunner = self.config.AlwaysResetRunner
        init_proto.WaitForJobsTimeoutSeconds = self.crop_gen_job.waitForJobsTimeoutSeconds

        apsim_config_proto = ApsimConfig_pb2.ApsimConfigProto()

        for input in self.crop_gen_job.inputs:
            apsim_config_proto.Inputs.append(input.name)

        if self.crop_gen_job.get_is_environment_typing_run():
            apsim_config_proto.SystemPropertyNames.append(self.config.ApsimClockStartDateYearInputName)
            apsim_config_proto.SystemPropertyNames.append(self.config.ApsimClockEndDateYearInputName)

        report_config_proto = apsim_config_proto.ReportDetails.add()
        report_config_proto.ReportName = self.crop_gen_job.reportName

        for output in self.crop_gen_job.outputs:
            report_config_proto.Fields.append(output.apsimOutputName)

        init_proto.Configuration.CopyFrom(apsim_config_proto)

        return init_proto

    @staticmethod
    def get_response_type() -> type:
        return InitApsimResponse

    @staticmethod
    def get_type_name():
        return __class__.__name__ + "Proto"