import json
import logging

from lib.models.cgm.relay_apsim import RelayApsim
from lib.problems.problem_base import ProblemBase
from lib.utils.apsim_season_date_generator import APSIMSeasonDateGenerator
from lib.utils.constants import Constants
from lib.utils.date_time_helper import DateTimeHelper

#
# Represents an Environment Typing Problem
#
class EnvironmentTypingProblem(ProblemBase):

    #
    # Construct problem with the given dimensions and variable ranges
    #
    def __init__(self, config, run_job_request, cgm_server_client):
        logging.info("%s has received a request for an Environment Typing run.", Constants.APPLICATION_NAME)
        super().__init__(config, run_job_request, cgm_server_client)

    #
    # Iterate over each population and perform calculations
    #
    def _evaluate(self, variable_values_for_population, out_objective_values, *args, **kwargs):
        if self.run_errors:
            super()._initialize_algorithm_array(out_objective_values)
            return

        super()._log_processing_iteration(len(variable_values_for_population))

        start_time = DateTimeHelper.get_date_time()

        response = self._perform_relay_apsim_request(variable_values_for_population)
        self._log_results_for_simulations(response)

        if not super()._handle_evaluate_value_for_population(response, out_objective_values, variable_values_for_population):
            super()._initialize_algorithm_array(out_objective_values)
            return

        super()._log_time_remaining(start_time)

        # Increment our iteration ID.
        self.current_iteration_id += 1

    #
    # Creates request(s) and runs apsim.
    #
    def _perform_relay_apsim_request(self, variable_values_for_population):
        season_date_generator = APSIMSeasonDateGenerator(self.config, self.run_job_request.APSIMSimulationClockStartDate)
        relay_apsim_request = RelayApsim(self.run_job_request.JobID, self.run_job_request.Individuals)
        relay_apsim_request.add_inputs_for_env_typing(self.run_job_request.EnvironmentTypes, season_date_generator, variable_values_for_population)
        response = super()._call_relay_apsim(relay_apsim_request)
        return response
    
    #
    # Logs the results for the simulations so that we can easily see the returned seasons.
    #
    def _log_results_for_simulations(self, response):
        if not response: return
        results_dict = {}

        for row in response.Rows:
            simulation_name = row.SimulationName
            if simulation_name not in results_dict:
                results_dict[simulation_name] = []
            results_dict[simulation_name].append({
                "SimulationID": row.SimulationID,
                "Values": row.Values
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
