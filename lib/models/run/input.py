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
        self.Name = name
        self.Min = min
        self.Max = max

    #
    # Parses the inputs
    #
    @staticmethod
    def parse_inputs(json_object, errors):
        inputs = JsonHelper.get_attribute(json_object, 'inputs', errors)

        if not inputs:
            errors.append("No inputs supplied.")
            return []
        
        parsed_inputs = [] 
        for input_value in inputs:
            name = JsonHelper.get_attribute(input_value, 'name', errors)
            min = JsonHelper.get_attribute(input_value, 'min', errors)
            max = JsonHelper.get_attribute(input_value, 'max', errors)

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