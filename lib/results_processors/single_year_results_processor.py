from lib.problems.output_value import OutputValue
from lib.problems.apsim_output import ApsimOutput

#
# Helper for processing the single year results.
#
class SingleYearResultsProcessor():
    
    #
    # Handles the results for a single year sim.
    #
    @staticmethod
    def process_results(
        crop_gen_job,
        results_for_individual,
        all_algorithm_outputs,
        all_results_outputs
    ):
        assert(len(results_for_individual) == 1)
        apsim_result = results_for_individual[0]

        total_outputs = min(crop_gen_job.get_total_outputs(), len(apsim_result.values))
        algorithm_outputs = []

        apsim_output = ApsimOutput(apsim_result.simulationID, apsim_result.simulationName)

        for output_index in range(0, total_outputs):
            raw_apsim_output = apsim_result.values[output_index]
            request_output = crop_gen_job.get_output_by_index(output_index)
            
            # If there is no output move onto the next one.
            if not request_output: continue

            if request_output.aggregateFunctions:
                raise Exception(f"Aggregate Functions configured but Apsim Job ID: {crop_gen_job.apsimJobId} is a single year APSIM simulation.")

            output_value = OutputValue(
                raw_apsim_output, 
                request_output.apsimOutputName, 
                request_output.maximise, 
                request_output.multiplier
            )
            
            # If we're optimising this value then we need to store it in the algorithm outputs.
            if request_output.optimise:
                algorithm_outputs.append(output_value.get_output_value_for_algorithm())

            apsim_output.outputs.append(output_value)

        all_algorithm_outputs.append(algorithm_outputs)
        all_results_outputs.append(apsim_output)
