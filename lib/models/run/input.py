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
        inputs = JsonHelper.get_attribute(json_object, 'Inputs', errors)

        if not inputs:
            errors.append("No inputs supplied.")
            return []
        
        parsed_inputs = [] 
        for output_value in inputs:
            name = JsonHelper.get_attribute(output_value, 'Name', errors)
            min = JsonHelper.get_attribute(output_value, 'Min', errors)
            max = JsonHelper.get_attribute(output_value, 'Max', errors)

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