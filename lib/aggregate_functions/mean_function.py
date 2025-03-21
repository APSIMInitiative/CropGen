import logging

#
# Represents an mean aggregate function
#
class MeanFunction:
    #
    # Calculate the mean.
    #
    @staticmethod
    def calculate(results_for_individual, apsim_output_index):

        if not results_for_individual:
            return 0.0

        total = sum(apsim_result.values[apsim_output_index] for apsim_result in results_for_individual)
        return total / len(results_for_individual)
