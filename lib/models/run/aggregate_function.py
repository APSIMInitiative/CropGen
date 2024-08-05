from lib.models.common.model import Model
from lib.utils.json_helper import JsonHelper

#
# Represents an aggregate function that is sent as part of a run job request.
#
class AggregateFunction(Model):
    #
    # Constructor
    #
    def __init__(self, display_name, maximise, multiplier, calc_type, params):
        self.displayName = display_name
        self.maximise = maximise
        self.multiplier = multiplier
        self.calcType = calc_type
        self.params = params
        
    #
    # Get the param in the specified index, or None if it doesn't exist
    #
    def get_param_by_index(self, index, convert_to_lower=True):
        param = None
        if len(self.params) > index:
            param = self.params[index]
            if convert_to_lower == True:
                param = param.lower().strip()
        return param

    #
    # Parses the aggregate functions.
    #
    @staticmethod
    def parse_aggregate_functions(json_object, errors):
        aggregate_functions = JsonHelper.get_non_mandatory_attribute(json_object, 'aggregateFunctions', True, [])
        if aggregate_functions == None:
            return []

        parsed_aggregate_functions = [] 
        for aggregate_function in aggregate_functions:
            display_name = JsonHelper.get_attribute(aggregate_function, 'displayName', errors, True)
            maximise = JsonHelper.get_non_mandatory_attribute(aggregate_function, 'maximise', True, False)
            multiplier = JsonHelper.get_non_mandatory_attribute(aggregate_function, 'multiplier', True, 1)
            calc_type = JsonHelper.get_attribute(aggregate_function, 'calcType', errors, True)
            params = JsonHelper.get_non_mandatory_attribute(aggregate_function, 'params', True, [])

            parsed_aggregate_functions.append(AggregateFunction(
                display_name,
                maximise,
                multiplier,
                calc_type,
                params
            ))
            
        return parsed_aggregate_functions

    #
    # Returns the type name.
    #
    @staticmethod
    def get_type_name():
        return __class__.__name__