import logging

from lib.models.common.model import Model
from lib.problems.output_value import OutputValue
from lib.utils.date_time_helper import DateTimeHelper

#
# Represents the input
#
class InputOutput(Model):
    #
    # Constructor
    #
    def __init__(self, name, values):        
        self.Name = name
        self.Values = values

#
# The Final Results Message contains the final maximised/minimised output.
#
class FinalResultsMessage(Model):
    #
    # Constructor
    #
    def __init__(
            self, 
            run_job_request, 
            variable_values_non_dominated_individuals, 
            objective_values_non_dominated_individuals,
            is_multi_year, 
            processed_aggregated_outputs
        ):

        self.DateTime = DateTimeHelper.get_date_time_now_str()
        self.JobID = run_job_request.JobID
        self.Inputs = self._extract_inputs(run_job_request.Inputs, variable_values_non_dominated_individuals)
        if is_multi_year: 
            self.Outputs = self._extract_outputs_multi_year_sim(processed_aggregated_outputs, objective_values_non_dominated_individuals)
        else:
            self.Outputs = self._extract_outputs_single_year_sim(run_job_request.Outputs, objective_values_non_dominated_individuals)

    # Extracts all of the inputs from the minimise result
    #
    def _extract_inputs(self, job_request_inputs, variable_values_non_dominated_individuals):
        inputs = []
        id = 0

        if not self._check_input_lengths(job_request_inputs, variable_values_non_dominated_individuals):
            return inputs

        for input in job_request_inputs:
            results = []
            for result in variable_values_non_dominated_individuals[:, id]:
                results.append(result)

            inputs.append(InputOutput(input.Name, results))
            id += 1
        return inputs


    def _check_input_lengths(self, job_request_inputs, variable_values_non_dominated_individuals):
        job_request_input_length = len(job_request_inputs)
        algorithm_value_length = len(variable_values_non_dominated_individuals)
        
        if job_request_input_length > algorithm_value_length:
            logging.error("job_request_inputs and variable_values_non_dominated_individuals have different lengths.")
            logging.error("Length of job_request_inputs: %d", job_request_input_length)
            logging.error("Length of variable_values_non_dominated_individuals: %d", algorithm_value_length)
            logging.error("Contents of job_request_inputs: %s", job_request_inputs)
            logging.error("Contents of variable_values_non_dominated_individuals: %s", variable_values_non_dominated_individuals)
            return False
        return True

    #
    # Extracts all of the outputs from the minimise result
    #    
    def _extract_outputs_single_year_sim(self, job_request_outputs, objective_values_non_dominated_individuals):
        outputs = []
        id = 0
        for output in job_request_outputs:
            results = []

            if not output.Optimise: continue

            for result in objective_values_non_dominated_individuals[:, id]:
                output_value = OutputValue(
                    result, 
                    output.ApsimOutputName, 
                    output.Maximise, 
                    output.Multiplier
                )
                results.append(output_value.get_output_value_from_algorithm())
            outputs.append(InputOutput(output.ApsimOutputName, results))
            id += 1
        return outputs
    
    #
    # Extracts all of the outputs from the minimise result
    #    
    def _extract_outputs_multi_year_sim(self, processed_aggregated_outputs, objective_values_non_dominated_individuals):
        outputs = []
        id = 0
        for output in processed_aggregated_outputs:            
            results = []
            for result in objective_values_non_dominated_individuals[:, id]:
                output_value = OutputValue(
                    result, 
                    output.DisplayName, 
                    output.Maximise, 
                    output.Multiplier
                )
                results.append(output_value.get_output_value_from_algorithm())
            outputs.append(InputOutput(output.DisplayName, results))
            id += 1
        return outputs
    
    #
    # Returns the type name.
    #
    def get_type_name(self):
        return __class__.__name__