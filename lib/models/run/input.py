from lib.models.common.model import Model
from lib.utils.json_helper import JsonHelper

#
# Represents an input that is sent as part of a run job request.
#
class Input(Model):
    #
    # Constructor
    #
    def __init__(self, name, min, max):        
        self.name = name
        self.min = min
        self.max = max

    #
    # Parses the inputs
    #
    @staticmethod
    def parse_from_json_object(lower_case_json_data, errors):
        inputs = JsonHelper.get_attribute(lower_case_json_data, 'inputs', errors, True)

        if not inputs:
            errors.append("No inputs supplied.")
            return []
        
        parsed_inputs = [] 
        for input_value in inputs:
            name = JsonHelper.get_attribute(input_value, 'name', errors, True)
            min = JsonHelper.get_attribute(input_value, 'min', errors, True)
            max = JsonHelper.get_attribute(input_value, 'max', errors, True)

            parsed_inputs.append(Input(
                name, 
                min,
                max
            ))
            
        return parsed_inputs

    #
    # Returns the type name.
    #
    def get_type_name(self):
        return __class__.__name__