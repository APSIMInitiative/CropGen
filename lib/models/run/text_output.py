import re
from lib.models.common.model import Model
from lib.utils.json_helper import JsonHelper

class TextOutput(Model):

    def __init__(self, apsim_output_name, regex_pattern=None):
        self.apsimOutputName = apsim_output_name
        self.regexPattern = regex_pattern


    @staticmethod
    def parse_from_json_object(lower_case_json_data, errors):
        text_outputs = JsonHelper.get_attribute(lower_case_json_data, 'textOutputs', errors, True)

        if not text_outputs:
            return []

        parsed_text_outputs = []
        for output_value in text_outputs:
            apsim_output_name = JsonHelper.get_attribute(output_value, 'apsimOutputName', errors, True)
            regex_pattern = JsonHelper.get_non_mandatory_attribute(output_value, 'regexPattern', True, None)
            
            # Create a TextOutput object and append to list
            parsed_text_outputs.append(TextOutput(apsim_output_name, regex_pattern))

        return parsed_text_outputs
    

    def extract_match(self, text):
        if not self.regexPattern:
            return text

        match = re.match(self.regexPattern, text)
        if match:
            return match.group(1)

        return text
    

    @staticmethod
    def get_type_name():
        return __class__.__name__
