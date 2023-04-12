import logging

from lib.utils.constants import Constants

#
# Represents an failure risk aggregate function
#
class FailureRiskFunction:
    #
    # Calculate the failure risk.
    #
    @staticmethod
    def calculate(aggregate_function, results_for_individual):
        
        operator = aggregate_function.get_param_by_index(Constants.FAILURE_RISK_PARAM_OPERATOR)
        value = float(aggregate_function.get_param_by_index(Constants.FAILURE_RISK_PARAM_VALUE))

        if not operator: raise Exception(f"{Constants.FAILURE_RISK_AGGREGATE_FUNCTION_ERROR}. No operator at index: {Constants.FAILURE_RISK_PARAM_OPERATOR}")
        if not value: raise Exception(f"{Constants.FAILURE_RISK_AGGREGATE_FUNCTION_ERROR}. No value at index: {Constants.FAILURE_RISK_PARAM_VALUE}")
        if not FailureRiskFunction._is_supported_operator(operator): raise Exception(f"{Constants.FAILURE_RISK_AGGREGATE_FUNCTION_ERROR}. Unknown operator: '{operator}'")

        total_results_for_individuals = len(results_for_individual)

        logging.info("Calling %s for: '%d' individuals. Using operator: '%s' and value: '%f'",
            __class__.__name__, 
            total_results_for_individuals,
            operator,
            value
        )

        # Need to calculate the sum of our data set that is within the specified value.
        sum_within_operator_and_value = 0
        for result in results_for_individual:
            for result_value in result.Values:
                if FailureRiskFunction._test_failure_risk_result_in_range(result_value, operator, value):
                    sum_within_operator_and_value += 1
        result = sum_within_operator_and_value / total_results_for_individuals
        logging.info("Result: '%f'", result)

        return result
    
    #
    # Tests the operator is one that is supported.
    #
    @staticmethod
    def _is_supported_operator(operator):
        return (
            operator == Constants.FAILURE_RISK_PARAM_LESS_THAN or
            operator == Constants.FAILURE_RISK_PARAM_LESS_EQUAL or 
            operator == Constants.FAILURE_RISK_PARAM_GREATER_THAN or 
            operator == Constants.FAILURE_RISK_PARAM_GREATER_THAN_EQUAL or 
            operator == Constants.FAILURE_RISK_PARAM_EQUAL or 
            operator == Constants.FAILURE_RISK_PARAM_NOT_EQUAL
        )

    #
    # Tests that the failure risk is within the specified range.
    #
    @staticmethod
    def _test_failure_risk_result_in_range(result_value, operator, value):
        if operator == Constants.FAILURE_RISK_PARAM_LESS_THAN:
            if result_value < value:
                return True
        if operator == Constants.FAILURE_RISK_PARAM_GREATER_THAN_EQUAL:
            if result_value <= value:
                return True
        if operator == Constants.FAILURE_RISK_PARAM_GREATER_THAN:
            if result_value > value:
                return True
        if operator == Constants.FAILURE_RISK_PARAM_GREATER_THAN_EQUAL:
            if result_value >= value:
                return True
        if operator == Constants.FAILURE_RISK_PARAM_EQUAL:
            if result_value == value:
                return True
        if operator == Constants.FAILURE_RISK_PARAM_NOT_EQUAL:
            if result_value != value:
                return True
        return False
    
    #
    # Returns the type name.
    #
    def get_type_name(self):
        return __class__.__name__