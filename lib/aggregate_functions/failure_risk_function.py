import logging

#
# Represents an failure risk aggregate function
#
class FailureRiskFunction:

    FAILURE_RISK_PARAM_OPERATOR = 0
    FAILURE_RISK_PARAM_VALUE = 1

    FAILURE_RISK_PARAM_LESS_THAN = '<'
    FAILURE_RISK_PARAM_LESS_THAN_EQUAL = '<='
    FAILURE_RISK_PARAM_GREATER_THAN = '>'
    FAILURE_RISK_PARAM_GREATER_THAN_EQUAL = '>='
    FAILURE_RISK_PARAM_EQUAL = '=='
    FAILURE_RISK_PARAM_NOT_EQUAL = '!='

    #
    # Calculate the failure risk.
    #
    @staticmethod
    def calculate(aggregate_function, results_for_individual, apsim_output_index):
        
        operator = aggregate_function.get_param_by_index(FailureRiskFunction.FAILURE_RISK_PARAM_OPERATOR)
        value = float(aggregate_function.get_param_by_index(FailureRiskFunction.FAILURE_RISK_PARAM_VALUE))

        FailureRiskFunction.validate_operator_value(operator, value)

        total_results_for_individuals = len(results_for_individual)

        # Need to calculate the sum of our data set that is within the specified value.
        sum_within_operator_and_value = 0
        for apsim_result in results_for_individual:
            if FailureRiskFunction._test_failure_risk_result_in_range(apsim_result.values[apsim_output_index], operator, value):
                sum_within_operator_and_value += 1
        result = sum_within_operator_and_value / total_results_for_individuals

        return result
    
    #
    # Validates both the operator and value are valid.
    #
    @staticmethod
    def validate_operator_value(operator, value):
        if operator == None: 
            raise Exception(f"{FailureRiskFunction.FAILURE_RISK_AGGREGATE_FUNCTION_ERROR}. No operator at index: {FailureRiskFunction.FAILURE_RISK_PARAM_OPERATOR}")
        if value == None: 
            raise Exception(f"{FailureRiskFunction.FAILURE_RISK_AGGREGATE_FUNCTION_ERROR}. No value at index: {FailureRiskFunction.FAILURE_RISK_PARAM_VALUE}")
        if not FailureRiskFunction._is_supported_operator(operator): 
            raise Exception(f"{FailureRiskFunction.FAILURE_RISK_AGGREGATE_FUNCTION_ERROR}. Unknown operator: '{operator}'")
    
    #
    # Tests the operator is one that is supported.
    #
    @staticmethod
    def _is_supported_operator(operator):
        return (
            operator == FailureRiskFunction.FAILURE_RISK_PARAM_LESS_THAN or
            operator == FailureRiskFunction.FAILURE_RISK_PARAM_LESS_THAN_EQUAL or 
            operator == FailureRiskFunction.FAILURE_RISK_PARAM_GREATER_THAN or 
            operator == FailureRiskFunction.FAILURE_RISK_PARAM_GREATER_THAN_EQUAL or 
            operator == FailureRiskFunction.FAILURE_RISK_PARAM_EQUAL or 
            operator == FailureRiskFunction.FAILURE_RISK_PARAM_NOT_EQUAL
        )

    #
    # Tests that the failure risk is within the specified range.
    #
    @staticmethod
    def _test_failure_risk_result_in_range(result_value, operator, value):
        if operator == FailureRiskFunction.FAILURE_RISK_PARAM_LESS_THAN:
            return result_value < value
        elif operator == FailureRiskFunction.FAILURE_RISK_PARAM_LESS_THAN_EQUAL:
            return result_value <= value
        elif operator == FailureRiskFunction.FAILURE_RISK_PARAM_GREATER_THAN:
            return result_value > value
        elif operator == FailureRiskFunction.FAILURE_RISK_PARAM_GREATER_THAN_EQUAL:
            return result_value >= value
        elif operator == FailureRiskFunction.FAILURE_RISK_PARAM_EQUAL:
            return result_value == value
        elif operator == FailureRiskFunction.FAILURE_RISK_PARAM_NOT_EQUAL:
            return result_value != value
        else: 
            logging.error("Unknown operator '%s'", operator)

        return False
    
    #
    # Returns the type name.
    #
    @staticmethod
    def get_type_name():
        return __class__.__name__