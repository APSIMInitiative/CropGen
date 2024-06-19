import os
import logging

import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
dst_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'autogen'))
sys.path.append(dst_dir)
import InitApsim_pb2

# from lib.models.cgm.init_workers import InitWorkers
# from lib.models.cgm.init_workers_response import InitWorkersResponse
#from lib.problems.problem_visualisation import ProblemVisualisation
from lib.utils.date_time_helper import DateTimeHelper
from lib.utils.constants import Constants

# import autogen.ReportConfig_pb2 as ReportConfig_pb2
# import autogen.ApsimConfig_pb2 as ApsimConfig_pb2
#import autogen.InitApsim_pb2 as InitApsim_pb2

class JobRunner():
    #
    # Constructor
    #
    def __init__(self, config):
        self.config = config
        self.cgm_server_client = None

    #
    # Processes the run job request passed in from the websocket.
    #
    def run(self, job):        
        logging.info("Running job request for id: %s", job.id)        
        logging.info("Job request: %s", job.to_json(self.config.PrettyPrintJsonInLogs))

        run_start_time = DateTimeHelper.get_date_time()

        if not self._init_cgm(job, self.cgm_server_client):
            logging.error("Failed to initialise %s. Run message will not be processed.", Constants.CGM_SERVER)
            return

        # problem = ProblemVisualisation(self.config, run_job_request)
        
        # # Now run the problem code, pass in the CGM factory class for 
        # problem.run(cgm_server_client)

        # Log out how long the problem took to run.
        logging.info("Problem run finished. Time taken: '%s'. ID: '%s', JobID: '%s', ApsimJobID: '%s', Name: '%s', Iterations: '%d', Individuals: '%d'", 
            DateTimeHelper.get_elapsed_time_since(run_start_time),
            job.id,
            job.jobId,
            job.apsimJobId,
            job.name,
            job.iterations,
            job.individuals
        )

    #
    # Calls init on the CGM server and returns the response.
    #
    def _init_cgm(self, job, cgm_server_client):

        # Create an instance of the InitWorkersProto message
        init_proto = InitApsim_pb2.InitApsimProto()
        init_proto.JobID = job.jobId

        return False

        # # Create an init workers request, using the contents of the run_job_request.
        # init_workers_request = InitWorkers(run_job_request, self.config)
        # read_message_data = cgm_server_client.call_cgm(init_workers_request)
        # errors = cgm_server_client.validate_cgm_call(read_message_data, init_workers_request, 'InitWorkersResponse')

        # if errors: 
        #     logging.error(errors)
        #     return False
        
        # # Convert the raw socket data into a RunApsimResponse object.
        # response = InitWorkersResponse()
        # response.parse_from_json_string(read_message_data.message_wrapper.TypeBody)
        # logging.info("Received InitWorkersResponse: '%s'", response.to_json(self.config.PrettyPrintJsonInLogs))

        # if response.TotalWorkers < self.config.MinimumRequiredCGMWorkers:
        #     logging.error(f"{Constants.CGM_SERVER_INSUFFICIENT_WORKERS_AVAILABLE}. Available {response.TotalWorkers}. Minimum: {self.config.MinimumRequiredCGMWorkers}")
        #     return False
        
        # return True
