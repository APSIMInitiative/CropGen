from lib.models.model import Model
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
    def __init__(self, run_job_request, minimise_result, is_multi_year, processed_aggregated_outputs):
        self.DateTime = DateTimeHelper.get_date_time_now_str()
        self.JobID = run_job_request.JobID
        self.Inputs = self._extract_inputs(run_job_request.Inputs, minimise_result)
        if is_multi_year: 
            self.Outputs = self._extract_outputs_multi_year_sim(processed_aggregated_outputs, minimise_result)
        else:
            self.Outputs = self._extract_outputs_single_year_sim(run_job_request.Outputs, minimise_result)

    # Extracts all of the inputs from the minimise result
    #
    def _extract_inputs(self, job_request_inputs, minimize_result):
        # Variable values for non-dominated Individuals in the last generation
        minimize_result_x = minimize_result.X
        
        inputs = []
        id = 0
        for input in job_request_inputs:
            results = []
            for result in minimize_result_x[:, id]:
                results.append(result)

            inputs.append(InputOutput(input.Name, results))
            id += 1
        return inputs

    #
    # Extracts all of the outputs from the minimise result
    #    
    def _extract_outputs_single_year_sim(self, job_request_outputs, minimize_result):
        # Objective values for non-dominated Individuals in the last generation
        minimize_result_f = minimize_result.F
        
        outputs = []
        id = 0
        for output in job_request_outputs:
            results = []
            for result in minimize_result_f[:, id]:
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
    def _extract_outputs_multi_year_sim(self, processed_aggregated_outputs, minimize_result):
        # Objective values for non-dominated Individuals in the last generation
        minimize_result_f = minimize_result.F
        
        outputs = []
        id = 0
        for output in processed_aggregated_outputs:
            results = []
            for result in minimize_result_f[:, id]:
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