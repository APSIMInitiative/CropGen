import logging

from lib.problems.output_value import OutputValue
from lib.problems.apsim_output import ApsimOutput

#
# Helper for processing the single year results.
#
class EmptyResultsProcessor():
    
    #
    # Handles the results for an empty results response.
    #
    @staticmethod
    def process_results(
        individual,
        crop_gen_job,
        results_for_individual,
        all_algorithm_outputs,
        all_results_outputs
    ):
        assert(len(results_for_individual) == 1)

        logging.warn("Processing empty results for individual: '%d'", individual + 1)

        total_outputs = crop_gen_job.get_total_outputs()
        algorithm_outputs = []

        first_result = results_for_individual[0]
        apsim_output = ApsimOutput(first_result.simulationID, first_result.simulationName)

        for output_index in range(0, total_outputs):
            request_output = crop_gen_job.get_output_by_index(output_index)

            # If there is no output move onto the next one.
            if not request_output: continue

            for aggregate_function in request_output.AggregateFunctions:
                raw_output_value = 0
                output_value = OutputValue(
                    raw_output_value, 
                    aggregate_function.DisplayName, 
                    aggregate_function.Maximise, 
                    aggregate_function.Multiplier
                )

                # If we're optimising this value then we need to store it in the algorithm outputs.
            if request_output.Optimise:
                algorithm_outputs.append(output_value.get_output_value_for_algorithm())
            
            apsim_output.outputs.append(output_value)

        all_algorithm_outputs.append(algorithm_outputs)
        all_results_outputs.append(apsim_output)
        