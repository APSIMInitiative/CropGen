#
# System wide constants.
#
class Constants():
    APPLICATION_NAME = 'CropGen'
    
    # This represents the key for specifying the number of generations to run 
    # when performing a minimize function using Pymoo.
    MINIMIZE_CONSTRAINT_NUMBER_OF_GENERATIONS = 'n_gen'
    OBJECTIVE_VALUES_ARRAY_INDEX = 'F'
    CGM_RELAY_APP_NAME = "CGMRelay"

    # Calc functions    
    TYPE_MEAN = 'mean'
    TYPE_WEIGHTED_MEAN = 'weightedmean'
    TYPE_MEAN_AT_HIGH_LOW_PERCENTAGE_YEARS = 'meanathighlowpercentageyears'
    TYPE_WEIGHTED_MEAN_AT_HIGH_LOW_PERCENTAGE_YEARS = 'weightedmeanathighlowpercentageyears'
    TYPE_FAILURE_RISK = 'failurerisk'
    TYPE_WEIGHTED_FAILURE_RISK = 'weightedfailurerisk'
    
    # Error messages
    NO_APSIM_RESULT_FOR_INDIVIDUALS = "Couldn't find an APSIM result for a given individual."
    NO_APSIM_RESULTS = "No results have been returned from APSIM."
    AGGREGATE_FUNCTION_ERROR = 'Cannot perform aggregate function.'
    FAILURE_RISK_AGGREGATE_FUNCTION_ERROR = f"{AGGREGATE_FUNCTION_ERROR} - Type: '{TYPE_FAILURE_RISK}'"
    MEAN_AT_AGGREGATE_FUNCTION_ERROR = f"{AGGREGATE_FUNCTION_ERROR} - Type: '{TYPE_MEAN_AT_HIGH_LOW_PERCENTAGE_YEARS}'"

    INVALID_SIMULATION_ID = '-1'
    INVALID_SIMULATION_NAME = 'unknown'
