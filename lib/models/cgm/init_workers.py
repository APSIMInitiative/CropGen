from lib.models.common.model import Model

#
# Represents the initialise message request that is sent to the CGM server.
#
class InitWorkers(Model):

    #
    # Constructor
    #
    def __init__(self, run_job_request, config):
        self.JobID = run_job_request.JobID
        self.Url = run_job_request.ApsimUrl
        self.ReportName = run_job_request.ReportName
        self.InputTraits = run_job_request.get_input_names()
        self.SystemPropertyNames = run_job_request.get_system_property_names(config)
        self.Outputs = run_job_request.get_apsim_output_names()
        self.ResetRunner = run_job_request.get_should_reset_runner(config)
        self.PreRunSimulations = config.InitWorkersPreRunSimulations

    #
    # Returns the type name.
    #
    def get_type_name(self):
        return __class__.__name__