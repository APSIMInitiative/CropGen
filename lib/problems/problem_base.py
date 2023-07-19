from pymoo.core.problem import Problem
import logging
import numpy as np

from lib.models.rest.iteration_results_message import IterationResultsMessage
from lib.problems.single_year_results_processor import SingleYearResultsProcessor
from lib.problems.multi_year_results_processor import MultiYearResultsProcessor
from lib.problems.empty_results_processor import EmptyResultsProcessor
from lib.utils.constants import Constants
from lib.utils.results_publisher import ResultsPublisher
from lib.models.cgm.run_apsim_response import RunApsimResponse
from lib.models.cgm.relay_apsim import RelayApsim

#
# The base class for Problems, provides some useful problem specific functionality.
#
class ProblemBase(Problem):

    MAX_SIMULATION_NAMES_TO_LIST = 10

    #
    # Constructor
    #
    def __init__(self, config, run_job_request, cgm_server_client):
        # Member variables
        self.config = config
        self.run_job_request = run_job_request
        self.run_errors = []
        self.current_iteration_id = 1
        self.is_multi_year = False
        self.processed_aggregated_outputs = []
        self.apsim_simulation_names = set()
        self.apsim_simulation_names_str = ''
        self.apsim_simulation_ids = set()
        self.apsim_simulation_ids_str = ''

        self.results_publisher = ResultsPublisher(
            run_job_request.IterationResultsUrl,
            run_job_request.FinalResultsUrl,
            config
        )

        self.cgm_server_client = cgm_server_client
        
        total_inputs = run_job_request.get_total_inputs()
        total_outputs = run_job_request.get_total_outputs_for_optimisation()
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
        for input in self.run_job_request.Inputs:
            input_lower_bounds.append(input.Min)
        return input_lower_bounds
    
    #
    # Create the input lower bounds by using the values from the run job request
    # input min values.
    #
    def _construct_input_upper_bounds(self):
        input_upper_bounds = []
        for input in self.run_job_request.Inputs:
            input_upper_bounds.append(input.Max)
        return input_upper_bounds
    
    #
    # Tests whether the results actually contain any results.
    #
    def _get_contains_results_for_individual(self, results_for_individual):
        return (
            len(results_for_individual) > 0
            and results_for_individual[0]
            and results_for_individual[0].SimulationID != Constants.INVALID_SIMULATION_ID
            and results_for_individual[0].SimulationName != Constants.INVALID_SIMULATION_NAME
            and len(results_for_individual[0].Values) > 0
        )
    
    #
    # Tests whether the results actually contain any results.
    #
    def _get_contains_results(self, run_apsim_response):
        return (
            len(run_apsim_response.Rows) > 0
            and run_apsim_response.Rows[0]
            and run_apsim_response.Rows[0].SimulationID != Constants.INVALID_SIMULATION_ID
            and run_apsim_response.Rows[0].SimulationName != Constants.INVALID_SIMULATION_NAME
            and len(run_apsim_response.Rows[0].Values) > 0
        )
    
    #
    # Sets the is multi year flag and extract any aggregate functions if it is a multi year sim.
    #
    def _set_first_iteration_values(self, results_for_individual):
        self._set_unique_simulation_names(results_for_individual)
        
        if self.run_job_request.get_is_environment_typing_run() or len(results_for_individual) > 1:
            logging.info("%s is running a multi year simulation.", Constants.APPLICATION_NAME)
            self.is_multi_year = True
            self.processed_aggregated_outputs = []

            for output_index in range(0, self.run_job_request.get_total_outputs()):
                request_output = self.run_job_request.get_output_by_index(output_index)

                # If there is no output or we're not optimizing this output, then just skip and move onto the next one.
                if not request_output or not request_output.Optimise:
                    continue

                for aggregate_function in request_output.AggregateFunctions:
                    self.processed_aggregated_outputs.append(aggregate_function)
        else:
            logging.info("%s is running a single year simulation.", Constants.APPLICATION_NAME)
            self.is_multi_year = False

    #
    # Gets the unique simulation names from the results provided.
    #
    def _set_unique_simulation_names(self, results_for_individual):
        self.apsim_simulation_names = set()
        self.apsim_simulation_ids = set()
        for apsim_result in results_for_individual:
            self.apsim_simulation_names.add(apsim_result.SimulationName.strip())
            self.apsim_simulation_ids.add(apsim_result.SimulationID)

        total_apsim_simulations = len(self.apsim_simulation_names)

        if total_apsim_simulations > ProblemBase.MAX_SIMULATION_NAMES_TO_LIST:
            self.apsim_simulation_names_str = f"Multiple APSIM Simulations ({total_apsim_simulations})"
            self.apsim_simulation_ids_str = 0
        else:
            delimiter = ', '
            self.apsim_simulation_names_str = delimiter.join(self.apsim_simulation_names)
            self.apsim_simulation_ids_str = delimiter.join(self.apsim_simulation_names)

    #
    # This initializes the out array that has to be populated as part of the
    # minimize algorithm.
    #
    def _initialize_algorithm_array(self, out_objective_values):
        out_objective_values[Constants.OBJECTIVE_VALUES_ARRAY_INDEX] = np.empty(
            [self.run_job_request.Individuals, self.run_job_request.get_total_inputs()]
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
        relay_apsim_request,
        out_objective_values,
        variable_values_for_population
    ):
        response = self._call_relay_apsim(relay_apsim_request)
        if not response:
            return False

        # Populate the iteration message with all of the data that we currently have.
        iteration_results_message = IterationResultsMessage(self.run_job_request, self.current_iteration_id, variable_values_for_population)

        all_algorithm_outputs = []
        all_results_outputs = []
        total_inputs = self.run_job_request.Individuals

        # Iterate over all of the individuals.
        for individual in range(RelayApsim.INPUT_START_INDEX, total_inputs):
            results_for_individual = response.get_apsim_results_for_individual(individual)

            # This shouldn't happen, but just in case...
            if not results_for_individual:
                self.run_errors.append(
                    f'{Constants.NO_APSIM_RESULT_FOR_INDIVIDUALS}. Individual: {individual}. RunApsimResponse: {response.to_json(self.config.pretty_print_json_in_logs)}'
                )
                return False

            # The first time through we capture whether this is a multi or single year sim.
            if self.current_iteration_id == 1 and individual == RelayApsim.INPUT_START_INDEX:
                self._set_first_iteration_values(results_for_individual)

            logging.debug("Processing APSIM result for individual (%d of %d)", individual + 1, total_inputs)

            if not self._get_contains_results_for_individual(results_for_individual):
                EmptyResultsProcessor.process_results(individual, self.run_job_request, self.config, results_for_individual, all_algorithm_outputs, all_results_outputs)

            elif self.is_multi_year:
                MultiYearResultsProcessor.process_results(
                    self.run_job_request, 
                    self.config, 
                    self.apsim_simulation_names_str, 
                    self.apsim_simulation_ids_str, 
                    results_for_individual, 
                    all_algorithm_outputs, 
                    all_results_outputs
                )

            else:
                SingleYearResultsProcessor.process_results(self.run_job_request, results_for_individual, all_algorithm_outputs, all_results_outputs)

        # Feed the results back into the algorithm so that it can continue advancing...
        out_objective_values[Constants.OBJECTIVE_VALUES_ARRAY_INDEX] = np.array(all_algorithm_outputs)

        # Populate the iteration results with the outputs from each individual.
        iteration_results_message.add_outputs(self.run_job_request.get_display_output_names(), all_results_outputs)

        # Send out the results.
        self.results_publisher.publish_iteration_results(iteration_results_message)

        return True

    #
    # Call APSIM and return the APSIM Response.
    #
    def _call_relay_apsim(self, relay_apsim_request):
        # Call CGM which will in turn call APSIM.
        read_message_data = self.cgm_server_client.call_cgm(relay_apsim_request)
        self.run_errors = self.cgm_server_client.validate_cgm_call(read_message_data, 'RunApsimResponse')

        # If there were any errors then bail out (these errors are logged later on.)
        if self.run_errors:
            logging.error(self.run_errors)
            return None

        # Convert the raw socket data into a RunApsimResponse object.
        response = RunApsimResponse()
        response.parse_from_json_string(read_message_data.message_wrapper.TypeBody)
        logging.debug("Received %s: '%s'", response.get_type_name(), response.to_json(self.config.pretty_print_json_in_logs))

        if not self._get_contains_results(response):
            error = Constants.NO_APSIM_RESULTS
            self.run_errors.append(error)
            logging.error(error)
            return None

        return response
