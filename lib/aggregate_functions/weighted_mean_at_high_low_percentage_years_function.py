import logging

from lib.utils.constants import Constants
from lib.aggregate_functions.mean_at_high_low_percentage_years_function import MeanAtHighLowPercentageYears

#
# Represents an mean at high low percentage years aggregate function
#
class WeightedMeanAtHighLowPercentageYears:
    #
    # Calculate the mean.
    #
    @staticmethod
    def calculate(crop_gen_job, aggregate_function, results_for_individual, apsim_output_index, round_up_years):
        return MeanAtHighLowPercentageYears.calculate(aggregate_function, results_for_individual, apsim_output_index, round_up_years)
    