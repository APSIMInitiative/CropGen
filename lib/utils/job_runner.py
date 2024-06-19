import logging

from lib.utils.date_time_helper import DateTimeHelper
from lib.utils.constants import Constants
from lib.proto.init_apsim import InitApsim

class JobRunner():

    def __init__(self, config):
        self.config = config
        self.cgm_server_client = None


    def run(self, crop_gen_job):        
        logging.info("Running job request for id: %s", crop_gen_job.id)        
        logging.info("Job request: %s", crop_gen_job.to_json(self.config.PrettyPrintJsonInLogs))

        run_start_time = DateTimeHelper.get_date_time()

        if not self._init_cgm(crop_gen_job):
            logging.error("Failed to initialise %s. Run message will not be processed.", Constants.CGM_SERVER)
            return

        # problem = ProblemVisualisation(self.config, run_job_request)
        
        # # Now run the problem code, pass in the CGM factory class for 
        # problem.run(cgm_server_client)

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

        init_apsim = InitApsim(self.config)
        init_apsim_proto = init_apsim.to_proto(crop_gen_job)