import logging

from lib.aggregate_functions.failure_risk_function import FailureRiskFunction
from lib.aggregate_functions.weighted_function_helper import WeightedFunctionHelper

#
# Represents an failure risk aggregate function
#
class WeightedFailureRiskFunction:

    FAILURE_RISK_PARAM_OPERATOR = 2
    FAILURE_RISK_PARAM_VALUE = 3

    #
    # Calculate the failure risk.
    #
    @staticmethod
    def calculate(
        crop_gen_job,
        aggregate_function, 
        results_for_individual, 
        apsim_output_index,
        aggregated_data_state
    ):
        if not results_for_individual:
            logging.error("No results available for calculating WeightedFailureRiskFunction.")
            return 0.0

        operator = aggregate_function.get_param_by_index(WeightedFailureRiskFunction.FAILURE_RISK_PARAM_OPERATOR)
        value = float(aggregate_function.get_param_by_index(WeightedFailureRiskFunction.FAILURE_RISK_PARAM_VALUE))

        FailureRiskFunction.validate_operator_value(operator, value)

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
        
        total_results_for_individuals = len(proportional_yields)

        # Need to calculate the sum of our data set that is within the specified value.
        sum_within_operator_and_value = 0
        for apsim_result in proportional_yields:
            if FailureRiskFunction._test_failure_risk_result_in_range(apsim_result, operator, value):
                sum_within_operator_and_value += 1
        result = sum_within_operator_and_value / total_results_for_individuals

        return result
    
    #
    # Returns the type name.
    #
    @staticmethod
    def get_type_name():
        return __class__.__name__