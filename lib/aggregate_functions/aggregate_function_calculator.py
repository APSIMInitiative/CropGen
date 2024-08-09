import logging

from lib.utils.constants import Constants
from lib.aggregate_functions.failure_risk_function import FailureRiskFunction
from lib.aggregate_functions.mean_function import MeanFunction
from lib.aggregate_functions.mean_at_high_low_percentage_years_function import MeanAtHighLowPercentageYears

#
# Represents an aggregate function that is sent as part of a run job request.
#
class AggregateFunctionCalculator:
    #
    # Constructor
    #
    def __init__(self, config, apsim_simulation_names_str, aggregate_function):
        self.config = config
        self.apsim_simulation_names_str = apsim_simulation_names_str
        self.aggregate_function = aggregate_function
        

    #
    # Calculate the output value using the passed in values
    # for an individual and the specified calc type.
    #
    def calculate_output_value(self, results_for_individual, apsim_output_index):
        calc_type = self.aggregate_function.calcType.lower().strip()
        output_value = None
        
        if calc_type == Constants.TYPE_FAILURE_RISK:
            output_value = FailureRiskFunction.calculate(self.aggregate_function, results_for_individual, apsim_output_index)
        elif calc_type == Constants.TYPE_MEAN:
            output_value = MeanFunction.calculate(results_for_individual, apsim_output_index)
        elif calc_type == Constants.TYPE_MEAN_AT_HIGH_LOW_PERCENTAGE_YEARS:
            output_value = MeanAtHighLowPercentageYears.calculate(self.aggregate_function, results_for_individual, apsim_output_index, self.config.RoundUpYearsInMeanCalculation)
        else:
            logging.error("Unknown Aggregate Function calc_type supplied: %s", calc_type)

        return output_value
