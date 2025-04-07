import logging

#
# Represents an mean at high low percentage years aggregate function
#
class MeanAtHighLowPercentageYears:
    
    MEAN_AT_PARAM_HIGH_LOW = 0
    MEAN_AT_PARAM_PERCENT = 1
    MEAN_AT_PARAM_HIGHEST = 'highest'
    MEAN_AT_PARAM_LOWEST = 'lowest'


    @staticmethod
    def calculate(aggregate_function, results_for_individual, apsim_output_index, round_up_years):
        
        if not results_for_individual:
            logging.error("No results available for calculating weighted mean.")
            return 0.0
        
        total_years = len(results_for_individual)

        if total_years == 1:
            return results_for_individual[0].values[apsim_output_index]

        high_low = aggregate_function.get_param_by_index(MeanAtHighLowPercentageYears.MEAN_AT_PARAM_HIGH_LOW)
        percentage = float(aggregate_function.get_param_by_index(MeanAtHighLowPercentageYears.MEAN_AT_PARAM_PERCENT))

        MeanAtHighLowPercentageYears.validate_high_low_percentage(high_low, percentage)

        # Create a sorted list for these values.
        sorted_list = MeanAtHighLowPercentageYears.create_sorted_list(results_for_individual)
        years_of_interest = MeanAtHighLowPercentageYears._extract_years_of_interest(sorted_list, high_low, percentage, total_years, round_up_years)
        years_of_interest_length = len(years_of_interest)
        result = 0

        if years_of_interest_length > 0:
            result = sum(years_of_interest) / years_of_interest_length
            
        return result
    

    @staticmethod
    def validate_high_low_percentage(high_low, percentage):

        if high_low == None: 
            raise Exception(f"{MeanAtHighLowPercentageYears.MEAN_AT_AGGREGATE_FUNCTION_ERROR}. No high/low specifier at index: {MeanAtHighLowPercentageYears.MEAN_AT_PARAM_HIGH_LOW}")
        if percentage == None: 
            raise Exception(f"{MeanAtHighLowPercentageYears.MEAN_AT_AGGREGATE_FUNCTION_ERROR}. No percentage at index: {MeanAtHighLowPercentageYears.MEAN_AT_PARAM_PERCENT}")
        if not MeanAtHighLowPercentageYears._is_supported_high_low(high_low): 
            raise Exception(f"{MeanAtHighLowPercentageYears.MEAN_AT_AGGREGATE_FUNCTION_ERROR}. Unknown high/low specifier: '{high_low}'")
        if not MeanAtHighLowPercentageYears._is_supported_percentage(percentage): 
            raise Exception(f"{MeanAtHighLowPercentageYears.MEAN_AT_AGGREGATE_FUNCTION_ERROR}. Unknown percentage: '{percentage}'")
    
    @staticmethod
    def _is_supported_high_low(high_low):
        return (
            high_low == MeanAtHighLowPercentageYears.MEAN_AT_PARAM_HIGHEST or
            high_low == MeanAtHighLowPercentageYears.MEAN_AT_PARAM_LOWEST
        )
    
    
    @staticmethod
    def _is_supported_percentage(percentage):
        return (
            percentage >= 0.0 and
            percentage <= 100.0
        )
    

    @staticmethod
    def create_sorted_list(results_for_individual, apsim_output_index):
        sorted_list = list()
        for apsim_result in results_for_individual:
            sorted_list.append(apsim_result.values[apsim_output_index])
        sorted_list.sort()

        return sorted_list
    

    @staticmethod
    def _extract_years_of_interest(sorted_list, high_low, percentage, total_years, round_up_years):
        years = (total_years * (percentage/100))
        if round_up_years:
            years += 0.5
        years = int(years)

        if high_low == MeanAtHighLowPercentageYears.MEAN_AT_PARAM_LOWEST:
            return sorted_list[0:years]
        elif high_low == MeanAtHighLowPercentageYears.MEAN_AT_PARAM_HIGHEST:
            return sorted_list[-years:]
        else:
            logging.error("Unknown high_low '%s'", high_low)
        
        return None
