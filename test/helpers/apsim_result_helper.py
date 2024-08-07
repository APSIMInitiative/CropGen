from lib.proto.messages.apsim_result import ApsimResult

class ApsimResultHelper():
    @staticmethod
    def create_apsim_result(values):
        apsim_result = ApsimResult()
        apsim_result.values = values
        return apsim_result
    
    @staticmethod
    def create_results_for_individual(result_values, apsim_output_index):
        results_for_individual = []

        for result in range(0, len(result_values)):
            values = []
            for value in range(0, len(result_values)):
                if value == apsim_output_index:
                    values.append(result_values[result])
                else:
                    values.append(0)
            results_for_individual.append(ApsimResultHelper.create_apsim_result(values))

        return results_for_individual