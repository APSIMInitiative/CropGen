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

        total_results_for_individuals = len(results_for_individual)

        if total_results_for_individuals == 0:
            return 0

        # Need to calculate the sum of our data to obtain the mean.
        total = 0

        for apsim_result in results_for_individual:
            total += apsim_result.values[apsim_output_index]

        result = total / total_results_for_individuals
        
        return result
