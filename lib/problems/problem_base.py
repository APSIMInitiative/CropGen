from pymoo.core.problem import Problem
import numpy as np
import logging

from lib.server.iteration_result import IterationResult
from lib.results_processors.single_year_results_processor import SingleYearResultsProcessor
from lib.results_processors.multi_year_results_processor import MultiYearResultsProcessor
from lib.results_processors.empty_results_processor import EmptyResultsProcessor
from lib.utils.constants import Constants
#from lib.utils.results_publisher import ResultsPublisher
from lib.socket.proto_zmq_client import ProtoZMQClient
from lib.models.cgm.run_apsim_response import RunApsimResponse
from lib.models.cgm.relay_apsim import RelayApsim
from lib.utils.date_time_helper import DateTimeHelper

#
# The base class for Problems, provides some useful problem specific functionality.
#
class ProblemBase(Problem):
    #
    # Constructor
    #
    def __init__(self, config, crop_gen_job, cgm_relay_address, results_manager):
        self.config = config
        self.crop_gen_job = crop_gen_job
        self.run_errors = []
        self.current_iteration_id = 1
        self.is_multi_year = False
        self.processed_aggregated_outputs = []

        self.apsim_simulation_id_str = ''
        self.apsim_simulation_names = set()
        self.apsim_simulation_name_str = ''

        self.cgm_relay_address = cgm_relay_address
        self.zmq_client = ProtoZMQClient(config, self.cgm_relay_address, Constants.CGM_RELAY_SOCKET_SERVICE_PORT)
        self.results_manager = results_manager

        total_inputs = crop_gen_job.get_total_inputs()
        total_outputs = crop_gen_job.get_total_outputs_for_optimisation()
        lower_bounds = self._construct_input_lower_bounds()
        upper_bounds = self._construct_input_upper_bounds()

        logging.info(
            "Constructing Problem with %d inputs and %d outputs. Setting the lowerbounds to: %s and the upperbounds to: %s",
            total_inputs,
            total_outputs,
            lower_bounds,
            upper_bounds
        )

        super().__init__(
            n_var=total_inputs,
            n_obj=total_outputs,
            xl=np.array(lower_bounds),
            xu=np.array(upper_bounds)
        )

    #
    # Create the input lower bounds by using the values from the run job request
    # input min values.
    #
    def _construct_input_lower_bounds(self):
        input_lower_bounds = []
        for input in self.crop_gen_job.inputs:
            input_lower_bounds.append(input.min)
        return input_lower_bounds
    
    #
    # Create the input lower bounds by using the values from the run job request
    # input min values.
    #
    def _construct_input_upper_bounds(self):
        input_upper_bounds = []
        for input in self.crop_gen_job.inputs:
            input_upper_bounds.append(input.max)
        return input_upper_bounds
    
    #
    # Tests whether the results actually contain any results.
    #
    def _get_contains_results_for_individual(self, results_for_individual):
        return (
            len(results_for_individual) > 0
            and results_for_individual[0]
            and results_for_individual[0].simulationID != Constants.INVALID_SIMULATION_ID
            and results_for_individual[0].simulationName != Constants.INVALID_SIMULATION_NAME
            and len(results_for_individual[0].values) > 0
        )
    
    #
    # Tests whether the results actually contain any results.
    #
    def _get_contains_results(self, run_apsim_response):
        return (
            len(run_apsim_response.rows) > 0
            and run_apsim_response.rows[0]
            and run_apsim_response.rows[0].simulationID != Constants.INVALID_SIMULATION_ID
            and run_apsim_response.rows[0].simulationName != Constants.INVALID_SIMULATION_NAME
            and len(run_apsim_response.rows[0].values) > 0
        )
    
    #
    # Sets the is multi year flag and extract any aggregate functions if it is a multi year sim.
    #
    def _set_first_iteration_values(self, results_for_individual):
        self._set_unique_simulation_names(results_for_individual)
        
        if self.crop_gen_job.get_is_environment_typing_run() or len(results_for_individual) > 1:
            logging.info("%s is running a multi year simulation.", Constants.APPLICATION_NAME)
            self.is_multi_year = True
            self.processed_aggregated_outputs = []

            for output_index in range(0, self.crop_gen_job.get_total_outputs()):
                request_output = self.crop_gen_job.get_output_by_index(output_index)

                # If there is no output or we're not optimizing this output, then just skip and move onto the next one.
                if not request_output or not request_output.optimise:
                    continue

                for aggregate_function in request_output.aggregateFunctions:
                    self.processed_aggregated_outputs.append(aggregate_function)
        else:
            logging.info("%s is running a single year simulation.", Constants.APPLICATION_NAME)
            self.is_multi_year = False

    #
    # Gets the unique simulation names from the results provided.
    #
    def _set_unique_simulation_names(self, results_for_individual):
        self.apsim_simulation_names = set()
        
        for apsim_result in results_for_individual:
            self.apsim_simulation_names.add(apsim_result.simulationName.strip())
            self.apsim_simulation_id_str = apsim_result.simulationID

        total_apsim_simulations = len(self.apsim_simulation_names)

        if total_apsim_simulations > 1:
            self.apsim_simulation_name_str = f"{total_apsim_simulations} APSIM Simulations"
            self.apsim_simulation_id_str = 0
        else:
            delimiter = ', '
            self.apsim_simulation_name_str = delimiter.join(self.apsim_simulation_names)

    #
    # This initializes the out array that has to be populated as part of the
    # minimize algorithm.
    #
    def _initialize_algorithm_array(self, out_objective_values):
        out_objective_values[Constants.OBJECTIVE_VALUES_ARRAY_INDEX] = np.empty(
            [self.crop_gen_job.Individuals, self.crop_gen_job.get_total_inputs()]
        )

    #
    # Evaluate fitness of the Individuals in the population
    # Parameters:
    # - relay_apsim_request: This is the request that is sent to the CGM server. It contains all of the values from the population.
    # - out_objective_values(dict): The dictionary to write the objective values out to. 'F' key for objectives and 'G' key for constraints
    # - variable_values_for_population(list): The variable values (in lists) for each individual in the population
    #
    def _handle_evaluate_value_for_population(
        self,
        response,
        out_objective_values,
        variable_values_for_population
    ):
        if not response:
            return False

        # Populate the iteration message with all of the data that we currently have.
        iteration_results = IterationResult(self.crop_gen_job, self.current_iteration_id, variable_values_for_population)

        all_algorithm_outputs = []
        all_results_outputs = []
        total_inputs = self.crop_gen_job.individuals

        # Iterate over all of the individuals.
        for individual in range(RelayApsim.INPUT_START_INDEX, total_inputs):
            results_for_individual = response.get_apsim_results_for_individual(individual)

            # This shouldn't happen, but just in case...
            if not results_for_individual:
                self.run_errors.append(
                    f'{Constants.NO_APSIM_RESULT_FOR_INDIVIDUALS}. Individual: {individual}. RunApsimResponse: {response.to_json(self.config.PrettyPrintJsonInLogs)}'
                )
                return False
            
            is_first = self.current_iteration_id == 1 and individual == RelayApsim.INPUT_START_INDEX

            # The first time through we capture whether this is a multi or single year sim.
            if is_first:
                self._set_first_iteration_values(results_for_individual)

            logging.debug("Processing APSIM result for individual (%d of %d)", individual + 1, total_inputs)

            if not self._get_contains_results_for_individual(results_for_individual):
                EmptyResultsProcessor.process_results(individual, self.crop_gen_job, results_for_individual, all_algorithm_outputs, all_results_outputs)

            elif self.is_multi_year:
                MultiYearResultsProcessor.process_results(
                    self.crop_gen_job, 
                    self.config, 
                    self.apsim_simulation_id_str, 
                    self.apsim_simulation_name_str,
                    results_for_individual, 
                    all_algorithm_outputs, 
                    all_results_outputs,
                    is_first
                )

            else:
                SingleYearResultsProcessor.process_results(self.crop_gen_job, results_for_individual, all_algorithm_outputs, all_results_outputs)

        # Feed the results back into the algorithm so that it can continue advancing...
        out_objective_values[Constants.OBJECTIVE_VALUES_ARRAY_INDEX] = np.array(all_algorithm_outputs)

        # Populate the iteration results with the outputs from each individual.
        iteration_results.add_outputs(self.crop_gen_job.get_display_output_names(), all_results_outputs)

        # Append the iteration result to our list of results.
        self.results_manager.add_iteration_result(iteration_results)

        return True

    #
    # Call APSIM and return the APSIM Response.
    #
    def _call_relay_apsim(self, relay_apsim_request):        
        run_apsim_response = self.zmq_client.send_proto_message(relay_apsim_request)

        logging.debug("Received %s: %s", run_apsim_response.get_type_name(), run_apsim_response.to_json(self.config.PrettyPrintJsonInLogs))

        if not self._get_contains_results(run_apsim_response):
            error = Constants.NO_APSIM_RESULTS
            self.run_errors.append(error)
            logging.error(error)
            return None

        return run_apsim_response

    #
    # Stitches multiple RunApsimResponses into one.
    #
    def _stitch_responses_together(self, responses):
        run_apsim_response = RunApsimResponse()

        for response in responses:            
            run_apsim_response.ID = response.ID

            if response.Fields:
                for field in response.Fields:
                    run_apsim_response.Fields.append(field)

            if response.Rows:
                for row in response.Rows:
                    run_apsim_response.Rows.append(row)

        return run_apsim_response
    
    #
    # Logs that we are processing a specific iteration.
    #
    def _log_processing_iteration(self, total_individuals):

        logging.info("Processing APSIM iteration (%d of %d) with %d individuals", 
            self.current_iteration_id, 
            self.crop_gen_job.iterations,
            total_individuals
        )
    
    #
    # Logs the remaining time.
    #
    def _log_time_remaining(self, start_time):
        seconds_taken_one_iteration = DateTimeHelper.get_elapsed_seconds_since(start_time)
        estimated_seconds_remaining = (self.crop_gen_job.iterations - self.current_iteration_id) * seconds_taken_one_iteration

        logging.info("Finished processing APSIM iteration: %d. Time taken: %s. %s",  
            self.current_iteration_id, 
            DateTimeHelper.seconds_to_hhmmss_ms(seconds_taken_one_iteration),
            self._generate_time_remaining_log(estimated_seconds_remaining)
        )

    #
    # Simple helper for generating the remaining time log, based on if it's the last iteration or not.
    #
    @staticmethod
    def _generate_time_remaining_log(estimated_seconds_remaining):
        if estimated_seconds_remaining > 0:
            return f"Estimated finish date time: {DateTimeHelper.add_seconds_to_datetime_now(estimated_seconds_remaining)} ({DateTimeHelper.seconds_to_hhmmss_ms(estimated_seconds_remaining)})"
        return "No more iterations to process..."
