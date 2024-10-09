import json
import logging

from lib.proto.messages.relay_apsim  import RelayApsim
from lib.problems.problem_base import ProblemBase
from lib.utils.apsim_season_date_generator import APSIMSeasonDateGenerator
from lib.utils.constants import Constants
from lib.utils.date_time_helper import DateTimeHelper
from lib.utils.array_utils import ArrayUtils

#
# Represents an Environment Typing Problem
#
class EnvironmentTypingProblem(ProblemBase):

    #
    # Construct problem with the given dimensions and variable ranges
    #
    def __init__(self, env_provider, config, crop_gen_job, cgm_relay_address, results_manager, memory_usage_tracker):
        logging.info("%s has received a request for an Environment Typing run.", Constants.APPLICATION_NAME)
        super().__init__(env_provider, config, crop_gen_job, cgm_relay_address, results_manager, memory_usage_tracker)

    #
    # Iterate over each population and perform calculations
    #
    def _evaluate(self, variable_values_for_population, out_objective_values, *args, **kwargs):
        if self.run_errors:
            super()._initialize_algorithm_array(out_objective_values)
            return

        super()._log_processing_iteration(len(variable_values_for_population))

        self.iteration_start_time = DateTimeHelper.get_date_time()

        response = self._perform_relay_apsim_request(variable_values_for_population)
        #self._log_results_for_simulations(response)

        if not super()._handle_evaluate_value_for_population(response, out_objective_values, variable_values_for_population):
            super()._initialize_algorithm_array(out_objective_values)
            return

    #
    # Creates request(s) and runs apsim.
    #
    def _perform_relay_apsim_request(self, variable_values_for_population):
        max_simulations = self.crop_gen_job.maxSimulationsPerRequest

        if (max_simulations and max_simulations > 0):
            return self._perform_relay_apsim_simulation_split(variable_values_for_population, max_simulations)
        else:
            return self._perform_relay_apsim_one_request(variable_values_for_population)

    #
    # Creates request(s) and runs apsim.
    #
    def _perform_relay_apsim_simulation_split(self, variable_values_for_population, max_simulations):
        split_environment_types = ArrayUtils._split_arr(self.crop_gen_job.environmentTypes, max_simulations)
        total_relay_apsim_requests = len(split_environment_types)

        logging.info("Relay Apsim requests are being split into %d requests. MaxSimulations has been set to: %d. TotalSimulations: %d", 
            total_relay_apsim_requests,
            max_simulations,
            len(self.crop_gen_job.environmentTypes)
        )
        
        responses = []
        current_relay_apsim_request = 1
        season_date_generator = APSIMSeasonDateGenerator(self.config, self.crop_gen_job.apsimSimulationClockStartDate)

        for environment_types in split_environment_types:

            relay_apsim_request = RelayApsim(self.crop_gen_job.jobId, self.crop_gen_job.individuals)
            relay_apsim_request.add_inputs_for_env_typing(environment_types, season_date_generator, variable_values_for_population)
            unique_simulation_names = list({name[1] for name in relay_apsim_request.simulationNames})
            seasons = [season for env_type in environment_types 
                  for env in env_type.Environments 
                  for season in env.Seasons]
            
            logging.info("Relay Apsim request %d of %d. Iteration: %d. SimulationNames: %s. Total Inputs for request: %d (TotalSimulationYears: '%d' (from %d simulations) X TotalIndividuals: '%d' )", 
                current_relay_apsim_request,
                total_relay_apsim_requests,
                self.current_iteration_id,
                ",".join(unique_simulation_names),
                len(relay_apsim_request.inputs),
                len(seasons),                
                max_simulations,
                self.crop_gen_job.individuals
            )

            # Call relay apsim for the current chunk and store the response
            response = self._call_relay_apsim(relay_apsim_request)
            if not response: return None
            responses.append(response)

            current_relay_apsim_request += 1        

        response = super()._stitch_responses_together(responses)
        return response
    
    #
    # Creates request and runs apsim.
    #
    def _perform_relay_apsim_one_request(self, variable_values_for_population):

        season_date_generator = APSIMSeasonDateGenerator(self.config, self.crop_gen_job.apsimSimulationClockStartDate)
        relay_apsim_request = RelayApsim(self.crop_gen_job.jobId, self.crop_gen_job.individuals)
        relay_apsim_request.add_inputs_for_env_typing(self.crop_gen_job.environmentTypes, season_date_generator, variable_values_for_population)
        run_apsim_response = super()._call_relay_apsim(relay_apsim_request)
        return run_apsim_response
    
    #
    # Logs the results for the simulations so that we can easily see the returned seasons.
    #
    def _log_results_for_simulations(self, response):
        if not response: return
        results_dict = {}

        for row in response.rows:
            simulation_name = row.simulationName
            if simulation_name not in results_dict:
                results_dict[simulation_name] = []
            results_dict[simulation_name].append({
                "SimulationID": row.simulationID,
                "Values": row.values
            })

        try:
            # Convert the dictionary to JSON and pretty print it
            json_str = json.dumps(results_dict, indent=4)
        except Exception as e:
            logging.error("Error occurred while converting dictionary to JSON:")
            logging.error(str(e))
            return

        logging.debug("Environment Typing Sorted Results:")
        logging.debug(json_str)
