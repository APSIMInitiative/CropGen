from lib.models.common.model import Model
from lib.models.run.aggregate_function import AggregateFunction
from lib.utils.json_helper import JsonHelper

#
# Represents a text output that is sent as part of a job request.
#
class TextOutput(Model):
    #
    # Constructor
    #
    def __init__(self, apsim_output_name, regex_pattern):
        self.apsimOutputName = apsim_output_name
        self.regex_pattern = regex_pattern

    #
    # Parses the text outputs
    #
    @staticmethod
    def parse_from_json_object(lower_case_json_data, errors):
        text_outputs = JsonHelper.get_attribute(lower_case_json_data, 'textOutputs', errors, True)

        if not text_outputs:
            return []

        parsed_text_outputs = []
        for output_value in text_outputs:
            apsim_output_name = JsonHelper.get_attribute(output_value, 'apsimOutputName', errors, True)            
            regex_pattern = JsonHelper.get_non_mandatory_attribute(output_value, 'regexPattern', True, "")
            
            parsed_text_outputs.append(TextOutput(apsim_output_name, regex_pattern))
            
        return parsed_text_outputs

    #
    # Returns the type name.
    #
    @staticmethod
    def get_type_name():
        return __class__.__name__