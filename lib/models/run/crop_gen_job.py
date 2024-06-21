from lib.models.common.model import Model
from lib.models.run.input import Input
from lib.models.run.output import Output
from lib.utils.json_helper import JsonHelper

#
# Model that represents a run job request sent from the jobs server
#
class CropGenJob(Model):
    #
    # Constructor.
    #
    def __init__(self):
        self.id = ''
        self.jobId = ''
        self.name = ''
        self.iterations = 0
        self.individuals = 0
        self.reportName = ''
        self.inputs = []
        self.outputs = []
        self.apsimJobId = ''

    #
    # Parses the JSON data into this class.
    #
    def parse_from_json_string(self, json_object):
        errors = []
        try:
            required_attributes = [
                'id', 'jobId', 'name', 'iterations', 'individuals', 'reportName', 'apsimJobId'
            ]

            # Process required attributes
            for attribute in required_attributes:
                attribute_value = JsonHelper.get_attribute(json_object, attribute, errors)
                setattr(self, attribute, attribute_value)

            # Process Inputs and Outputs
            self.inputs = Input.parse_inputs(json_object, errors)
            self.outputs = Output.parse_outputs(json_object, errors)

        except Exception as error:
            errors.append(f"Failed to parse {self.__class__.__name__} JSON: '{json_object}'. Error: '{error}'")

        return errors
    
    #
    # Returns the type name.
    #
    def get_type_name(self):
        return __class__.__name__
