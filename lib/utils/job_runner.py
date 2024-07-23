import logging

from lib.utils.date_time_helper import DateTimeHelper
from lib.utils.constants import Constants
from lib.proto.messages.init_apsim_request import InitApsimRequest
from lib.socket.proto_zmq_client import ProtoZMQClient
from lib.problems.problem_visualisation import ProblemVisualisation

class JobRunner():

    def __init__(self, config, cgm_relay_address, results_manager):
        self.config = config
        self.cgm_relay_address = cgm_relay_address
        self.results_manager = results_manager
        self.zmq_client = ProtoZMQClient(config, self.cgm_relay_address, Constants.CGM_RELAY_SOCKET_SERVICE_PORT)


    def run(self, crop_gen_job):
        logging.info("Running job request for id: %s", crop_gen_job.id)        
        logging.info("Job request: %s", crop_gen_job.to_json(self.config.PrettyPrintJsonInLogs))

        run_start_time = DateTimeHelper.get_date_time()

        if not self._init_cgm(crop_gen_job):
            logging.error("Failed to initialise %s. Run message will not be processed.", Constants.CGM_SERVER)
            return

        problem = ProblemVisualisation(self.config, crop_gen_job, self.cgm_relay_address, self.results_manager)
        
        # Now run the problem code, pass in the CGM factory class for 
        problem.run()

        self.results_manager.write_to_disk()

        # Log out how long the problem took to run.
        logging.info("Problem run finished. Time taken: '%s'. ID: '%s', JobID: '%s', ApsimJobID: '%s', Name: '%s', Iterations: '%d', Individuals: '%d'", 
            DateTimeHelper.get_elapsed_time_since(run_start_time),
            crop_gen_job.id,
            crop_gen_job.jobId,
            crop_gen_job.apsimJobId,
            crop_gen_job.name,
            crop_gen_job.iterations,
            crop_gen_job.individuals
        )


    def _init_cgm(self, crop_gen_job):
        init_apsim = InitApsimRequest(self.config, crop_gen_job)
        init_apsim_response = self.zmq_client.send_proto_message(init_apsim)
        logging.info("Received %s: %s", init_apsim_response.get_type_name(), init_apsim_response.to_json(self.config.PrettyPrintJsonInLogs))
        return init_apsim_response != None
