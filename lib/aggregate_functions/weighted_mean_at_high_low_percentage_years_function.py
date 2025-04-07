import logging
import numpy as np

from lib.utils.constants import Constants
from lib.aggregate_functions.mean_at_high_low_percentage_years_function import MeanAtHighLowPercentageYears
from lib.aggregate_functions.weighted_function_helper import WeightedFunctionHelper
from lib.aggregate_functions.aggregated_data_state import AggregatedDataState


class WeightedMeanAtHighLowPercentageYears:

    MEAN_AT_PARAM_HIGH_LOW = 2
    MEAN_AT_PARAM_PERCENT = 3

    @staticmethod
    def calculate(
        crop_gen_job, 
        aggregate_function, 
        results_for_individual, 
        apsim_output_index, 
        round_up_years,
        aggregated_data_state
    ):
        if not results_for_individual:
            logging.error("No results available for calculating weighted mean.")
            return 0.0
        
        total_years = len(results_for_individual)

        if total_years == 1:
            return results_for_individual[0].values[apsim_output_index]

        high_low = aggregate_function.get_param_by_index(WeightedMeanAtHighLowPercentageYears.MEAN_AT_PARAM_HIGH_LOW)
        percentage = float(aggregate_function.get_param_by_index(WeightedMeanAtHighLowPercentageYears.MEAN_AT_PARAM_PERCENT))

        MeanAtHighLowPercentageYears.validate_high_low_percentage(high_low, percentage)

        proportional_yields = WeightedFunctionHelper.get_or_compute_proportional_yields(
            crop_gen_job,
            aggregate_function,
            results_for_individual,
            apsim_output_index,
            aggregated_data_state
        )

        if not proportional_yields:
            logging.error("No proportional yields available for calculating weighted mean.")
            return 0.0
        
        # Create a sorted list for these values.
        sorted_list = MeanAtHighLowPercentageYears._extract_years_of_interest(proportional_yields, apsim_output_index, high_low, percentage, total_years, round_up_years)
        sorted_list_length = len(sorted_list)
        result = 0

        if sorted_list_length > 0:
            result = sum(sorted_list) / sorted_list_length
            
        return result
