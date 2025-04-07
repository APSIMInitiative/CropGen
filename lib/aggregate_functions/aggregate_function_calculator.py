import logging

from lib.utils.constants import Constants
from lib.aggregate_functions.mean_function import MeanFunction
from lib.aggregate_functions.weighted_mean_function import WeightedMeanFunction
from lib.aggregate_functions.mean_at_high_low_percentage_years_function import MeanAtHighLowPercentageYears
from lib.aggregate_functions.weighted_mean_at_high_low_percentage_years_function import WeightedMeanAtHighLowPercentageYears

#
# Represents an aggregate function that is sent as part of a run job request.
#
class AggregateFunctionCalculator:
    #
    # Constructor
    #
    def __init__(
        self, 
        config, 
        crop_gen_job, 
        apsim_simulation_names_str, 
        aggregate_function,
        aggregated_data_state
    ):
        self.config = config
        self.crop_gen_job = crop_gen_job
        self.apsim_simulation_names_str = apsim_simulation_names_str
        self.aggregate_function = aggregate_function
        self.aggregated_data_state = aggregated_data_state

    #
    # Calculate the output value using the passed in values
    # for an individual and the specified calc type.
    #
    def calculate_output_value(self, results_for_individual, apsim_output_index):
        calc_type = self.aggregate_function.calcType.lower().strip()
        output_value = None

        calc_functions = {
            Constants.TYPE_MEAN: 
                lambda: MeanFunction.calculate(
                    results_for_individual, 
                    apsim_output_index
                ),

            Constants.TYPE_WEIGHTED_MEAN: 
                lambda: WeightedMeanFunction.calculate(
                    self.crop_gen_job, 
                    self.aggregate_function, 
                    results_for_individual, 
                    apsim_output_index,
                    self.aggregated_data_state
                ),

            Constants.TYPE_MEAN_AT_HIGH_LOW_PERCENTAGE_YEARS: 
                lambda: MeanAtHighLowPercentageYears.calculate(
                    self.aggregate_function, 
                    results_for_individual, 
                    apsim_output_index, 
                    self.config.RoundUpYearsInMeanCalculation
                ),

            Constants.TYPE_WEIGHTED_MEAN_AT_HIGH_LOW_PERCENTAGE_YEARS: 
                lambda: WeightedMeanAtHighLowPercentageYears.calculate(
                    self.crop_gen_job, 
                    self.aggregate_function,
                    results_for_individual, 
                    apsim_output_index, 
                    self.config.RoundUpYearsInMeanCalculation,
                    self.aggregated_data_state
                )
        }

        # Get the corresponding function from the dictionary or log error if not found
        calc_func = calc_functions.get(calc_type)
        if calc_func:
            output_value = calc_func()
        else:
            logging.error("Unknown Aggregate Function calc_type supplied: %s", calc_type)

        return output_value
