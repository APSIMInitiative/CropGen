import logging

from lib.utils.date_time_helper import DateTimeHelper
from lib.utils.constants import Constants
from lib.proto.messages.init_apsim_request import InitApsimRequest
from lib.socket.proto_zmq_client import ProtoZMQClient
from lib.problems.problem_visualisation import ProblemVisualisation
from lib.utils.date_time_helper import DateTimeHelper
from lib.server.results_manager import ResultsManager
from lib.utils.constants import Constants

class JobRunner():

    def __init__(self, env_provider, config, server_state, cgm_relay_address, crop_gen_job):
        self.env_provider = env_provider
        self.config = config
        self.cgm_relay_address = cgm_relay_address
        self.crop_gen_job = crop_gen_job
        self.results_manager = ResultsManager(self.config, server_state, crop_gen_job)
        self.zmq_client = ProtoZMQClient(config, self.cgm_relay_address, env_provider.get_cgm_relay_socket_service_port())


    def run(self):
        logging.info("Running CropGenJob: '%s' (JobID: %s)", self.crop_gen_job.name, self.crop_gen_job.id)        
        logging.info("Job request: %s", self.crop_gen_job.to_json(self.config.PrettyPrintJsonInLogs))

        run_start_time = DateTimeHelper.get_date_time()

        if not self._init_cgm(self.crop_gen_job):
            logging.error("Failed to initialise %s. Run message will not be processed.", Constants.CGM_SERVER)
            return

        problem = ProblemVisualisation(self.env_provider, self.config, self.crop_gen_job, self.cgm_relay_address, self.results_manager)
        
        # Now run the problem code, pass in the CGM factory class for 
        problem.run()

        results_dir = self.results_manager.write_to_disk()

        # Log out how long the problem took to run.
        logging.info("Problem run finished. Results: %s. Time taken: '%s'. ID: '%s', JobID: '%s', ApsimJobID: '%s', Name: '%s', Iterations: '%d', Individuals: '%d'. Results saved here: '%s'", 
            self.results_manager.result_dir,
            DateTimeHelper.get_elapsed_time_since(run_start_time),
            self.crop_gen_job.id,
            self.crop_gen_job.jobId,
            self.crop_gen_job.apsimJobId,
            self.crop_gen_job.name,
            self.crop_gen_job.iterations,
            self.crop_gen_job.individuals,
            results_dir
        )


    def _init_cgm(self, crop_gen_job):
        init_apsim = InitApsimRequest(self.config, crop_gen_job)
        init_apsim_response = self.zmq_client.send_proto_message(init_apsim)
        logging.info("Received %s: %s", init_apsim_response.get_type_name(), init_apsim_response.to_json(self.config.PrettyPrintJsonInLogs))
        return init_apsim_response != None
