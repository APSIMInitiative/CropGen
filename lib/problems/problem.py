import logging

from lib.models.cgm.relay_apsim import RelayApsim
from lib.problems.problem_base import ProblemBase
from lib.config.apsim_simulation_data import APSimSimulationData
from lib.utils.date_time_helper import DateTimeHelper
from lib.utils.array_utils import ArrayUtils

#
# Represents a Problem
#
class Problem(ProblemBase):

    #
    # Construct problem with the given dimensions and variable ranges
    #
    def __init__(self, config, run_job_request, cgm_server_client):
        super().__init__(config, run_job_request, cgm_server_client)

    #
    # Iterate over each population and perform calculations.
    #
    def _evaluate(self, variable_values_for_population, out_objective_values, *args, **kwargs):
        if self.run_errors:
            super()._initialize_algorithm_array(out_objective_values)
            return

        super()._log_processing_iteration(len(variable_values_for_population))

        start_time = DateTimeHelper.get_date_time()

        response = self._perform_relay_apsim_request(variable_values_for_population)

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

        max_simulations = self.run_job_request.MaxSimulationsPerRequest
        apsim_data = APSimSimulationData()
        simulation_names = apsim_data.get_simulation_names(self.run_job_request.JobID)

        if (max_simulations and
            max_simulations > 0
        ):
            # If we're being asked to split the simulation names up, but there is no simulation names configured, throw.
            if not simulation_names: 
                raise Exception(f"MaxSimulations set but cannot find simulation names for JobID: {self.run_job_request.JobID}")

            return self._perform_relay_apsim_staggered_requests(variable_values_for_population, simulation_names, max_simulations)
        else:
            return self._perform_relay_apsim_one_request(variable_values_for_population)
    
    #
    # Creates request(s) and runs apsim.
    #
    def _perform_relay_apsim_staggered_requests(self, variable_values_for_population, simulation_names, max_simulations):
        split_simulation_names = ArrayUtils._split_arr(simulation_names, max_simulations)
        total_relay_apsim_requests = len(split_simulation_names)

        logging.info("Relay Apsim requests are being split into %d requests. MaxSimulations has been set to: %d. TotalSimulations: %d", 
            total_relay_apsim_requests,
            max_simulations,
            len(simulation_names)
        )

        # Initialize an empty list to store the responses
        responses = []
              
        current_relay_apsim_request = 1

        for simulation_names in split_simulation_names:

            # Create a new RelayApsim object for each chunk
            relay_apsim_request = RelayApsim(self.run_job_request.JobID, len(variable_values_for_population))
           
            for simulation_name in simulation_names:
                individual = RelayApsim.INPUT_START_INDEX
                for input_index in range(len(variable_values_for_population)):
                    relay_apsim_request.add_inputs_for_individual(individual, variable_values_for_population[input_index])
                    relay_apsim_request.SimulationNames.append([str(input_index), simulation_name])
                    individual += 1

            logging.info("Relay Apsim request %d of %d. Iteration: %d. SimulationNames: %s. Total Inputs for request: %d", 
                current_relay_apsim_request,
                total_relay_apsim_requests,
                self.current_iteration_id,
                ",".join(simulation_names),
                len(relay_apsim_request.Inputs)
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
        
        relay_apsim_request = RelayApsim(self.run_job_request.JobID, len(variable_values_for_population))
        relay_apsim_request.add_inputs(variable_values_for_population)
        response = self._call_relay_apsim(relay_apsim_request)
        return response
