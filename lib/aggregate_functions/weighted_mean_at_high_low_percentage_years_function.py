import logging

from lib.aggregate_functions.mean_at_high_low_percentage_years_function import MeanAtHighLowPercentageYears
from lib.aggregate_functions.weighted_function_helper import WeightedFunctionHelper


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
            logging.error("No results available for calculating WeightedMeanAtHighLowPercentageYears.")
            return 0.0

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
        
        total_years = len(proportional_yields)

        if total_years == 1:
            return proportional_yields[0]
        
        # Create a sorted list for these values.
        proportional_yields.sort()
        years_of_interest = MeanAtHighLowPercentageYears._extract_years_of_interest(proportional_yields, high_low, percentage, total_years, round_up_years)
        years_of_interest_length = len(years_of_interest)
        result = 0

        if years_of_interest_length > 0:
            result = sum(years_of_interest) / years_of_interest_length
            
        return result        
