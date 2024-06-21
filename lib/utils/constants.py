#
# System wide constants.
#
class Constants():
    APPLICATION_NAME = 'CropGen'
    
    # This represents the key for specifying the number of generations to run 
    # when performing a minimize function using Pymoo.
    MINIMIZE_CONSTRAINT_NUMBER_OF_GENERATIONS = 'n_gen'
    OBJECTIVE_VALUES_ARRAY_INDEX = 'F'
    CGM_SERVER = 'CGM Server'
    CGM_RELAY_APP_NAME = "CGMRelay"
    CGM_RELAY_SOCKET_SERVICE_PORT = 5555

    # Messages - Comparisons are made after converting the value to test to lowercase.
    RUN_MESSAGE = 'runcropgen'
    STATUS_MESSAGE = 'status'
    GET_CONFIG_MESSAGE = 'getcropgenconfig'
    SET_CONFIG_MESSAGE = 'setcropgenconfig'

    # Calc functions
    TYPE_FAILURE_RISK = 'failurerisk'
    TYPE_MEAN = 'mean'
    TYPE_MEAN_AT_HIGH_LOW_PERCENTAGE_YEARS = 'meanathighlowpercentageyears'

    FAILURE_RISK_PARAM_OPERATOR = 0
    FAILURE_RISK_PARAM_VALUE = 1

    FAILURE_RISK_PARAM_LESS_THAN = '<'
    FAILURE_RISK_PARAM_LESS_THAN_EQUAL = '<='
    FAILURE_RISK_PARAM_GREATER_THAN = '>'
    FAILURE_RISK_PARAM_GREATER_THAN_EQUAL = '>='
    FAILURE_RISK_PARAM_EQUAL = '=='
    FAILURE_RISK_PARAM_NOT_EQUAL = '!='

    MEAN_AT_PARAM_HIGH_LOW = 0
    MEAN_AT_PARAM_PERCENT = 1
    MEAN_AT_PARAM_HIGHEST = 'highest'
    MEAN_AT_PARAM_LOWEST = 'lowest'

    # Error messages    
    CGM_SERVER_NO_DATA_READ = f'No data read from {CGM_SERVER}'
    CGM_SERVER_EXCEPTION = f'{CGM_SERVER} Exception'
    CGM_FAILED_TO_CONNECT_TO_CGM_SERVER = f'Failed to connect to {CGM_SERVER}'
    CGM_SERVER_NO_RESPONSE = f'No response from {CGM_SERVER}'
    CGM_SERVER_NO_RESPONSE_NO_EVALUATE = f"{CGM_SERVER_NO_RESPONSE}. Cannot handle evaluate"
    CGM_SERVER_INSUFFICIENT_WORKERS_AVAILABLE = f'{CGM_SERVER} - Insufficient "TotalWorkers" available to run job'
    CGM_SERVER_INVALID_RESPONSE = f"Invalid data returned from {CGM_SERVER}"
    CGM_SERVER_DISCONNECTED_WHILE_WAITING_FOR_RESPONSE = f"{CGM_SERVER} disconnected from socket whilst waiting for response"
    CGM_SERVER_ERROR_RESPONSE = f"Error response from {CGM_SERVER}"
    CGM_SERVER_TYPE_NAME_EXCEPTION_RESPONSE = 'ExceptionResponse'
    UNKNOWN_JOB_TYPE = 'Unknown run JobType'
    APSIM_RESULTS_NOT_EQUAL_TO_INDIVIDUALS = "Total APSIM results doesn't match the total requested individuals"
    NO_APSIM_RESULT_FOR_INDIVIDUALS = "Couldn't find an APSIM result for a given individual."
    NO_APSIM_RESULTS = "No results have been returned from APSIM."
    APSIM_OUTPUTS_NOT_EQUAL_TO_REQUESTED = "Total APSIM outputs doesn't match the total requested outputs"
    CROP_GEN_IS_ALREADY_RUNNING_A_JOB = 'CropGen is already running a job'
    UNKNOWN_TYPE_NAME = 'Unknown TypeName'
    AGGREGATE_FUNCTION_ERROR = 'Cannot perform aggregate function.'
    FAILURE_RISK_AGGREGATE_FUNCTION_ERROR = f"{AGGREGATE_FUNCTION_ERROR} - Type: '{TYPE_FAILURE_RISK}'"
    MEAN_AT_AGGREGATE_FUNCTION_ERROR = f"{AGGREGATE_FUNCTION_ERROR} - Type: '{TYPE_MEAN_AT_HIGH_LOW_PERCENTAGE_YEARS}'"

    INVALID_SIMULATION_ID = '-1'
    INVALID_SIMULATION_NAME = 'unknown'
