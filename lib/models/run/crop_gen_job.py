from lib.models.common.model import Model
from lib.models.run.input import Input
from lib.models.run.output import Output
from lib.models.run.environment_typing.simulation import Simulation
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
        self.apsimSimulationClockStartDate = ''
        self.environmentTypes = []
        self.maxSimulationsPerRequest = 0
        self.maxIndividualsPerRequest = 0
        self.errors = []

    #
    # Parses the JSON data into this class.
    #
    def parse_from_json_object(self, json_data):
        self.errors = []
        try:

            lower_case_json_data = self.convert_to_lower_case_recursive(json_data)

            self.id = JsonHelper.get_attribute(lower_case_json_data, 'id', self.errors)
            self.jobId = JsonHelper.get_attribute(lower_case_json_data, 'jobId', self.errors)
            self.name = JsonHelper.get_attribute(lower_case_json_data, 'name', self.errors)
            self.iterations = JsonHelper.get_attribute(lower_case_json_data, 'iterations', self.errors)
            self.individuals = JsonHelper.get_attribute(lower_case_json_data, 'individuals', self.errors)
            self.reportName = JsonHelper.get_attribute(lower_case_json_data, 'reportName', self.errors)
            self.apsimJobId = JsonHelper.get_attribute(lower_case_json_data, 'apsimJobId', self.errors)
            self.apsimSimulationClockStartDate = JsonHelper.get_attribute(lower_case_json_data, 'apsimSimulationClockStartDate', self.errors)
            self.maxSimulationsPerRequestd = JsonHelper.get_attribute(lower_case_json_data, 'maxSimulationsPerRequest', self.errors)
            self.maxIndividualsPerRequest = JsonHelper.get_attribute(lower_case_json_data, 'maxIndividualsPerRequest', self.errors)

            # Process Inputs and Outputs
            self.inputs = Input.parse_from_json_object(lower_case_json_data, self.errors)
            self.outputs = Output.parse_from_json_object(lower_case_json_data, self.errors)
            self.environmentTypes = self.parse_environment_types(lower_case_json_data, self.errors)

        except Exception as error:
            self.errors.append(f"Failed to parse {self.__class__.__name__} JSON: '{lower_case_json_data}'. Error: '{error}'")

    
    #
    # Helper function to parse the environment types.
    #
    @staticmethod
    def parse_environment_types(json_object, errors):
        environment_types = JsonHelper.get_non_mandatory_attribute(json_object, 'environmentTypes', [])

        if not environment_types: return []
        
        parsed_env_types = []

        for environment_type_value in environment_types:
            simulation = JsonHelper.get_attribute(environment_type_value, 'simulation', errors)
            parsed_env_types.append(Simulation.parse(simulation, errors))
            
        return parsed_env_types
    

    #
    # Simple helper for getting the total number of Inputs defined
    #
    def get_total_inputs(self):
        return len(self.inputs)

    #
    # Simple helper for getting the total number of outputs defined
    #
    def get_total_outputs(self):
        total_outputs = 0
        for output in self.outputs:
            total_aggregate_functions = len(output.aggregateFunctions)
            # Aggregate functions essentially expand out the amount of outputs
            # that we are handling.
            if total_aggregate_functions > 0:
                total_outputs += total_aggregate_functions
            else:
                total_outputs += 1
        return total_outputs
    
    #
    # Simple helper for getting the total number of outputs that have been defined as optimisable 
    #
    def get_total_outputs_for_optimisation(self):
        total_outputs = 0
        for output in self.outputs:
            if output.optimise:
                total_aggregate_functions = len(output.aggregateFunctions)
                # Aggregate functions essentially expand out the amount of outputs
                # that we are handling.
                if total_aggregate_functions > 0:
                    total_outputs += total_aggregate_functions
                else:
                    total_outputs += 1
        return total_outputs
    
    #
    # Get the output in the specified index, or None if it doesn't exist
    #
    def get_output_by_index(self, index):
        output = None
        if len(self.outputs) > index:
            return self.outputs[index]
        return output
    
    #
    # Extract the input names from the array of input objects.
    #
    def get_input_names(self):
        input_names = []
        for input in self.inputs:
            input_names.append(input.name)
        return input_names
    
    #
    # Extract the APSIM output names from the array of output objects.
    #
    def get_apsim_output_names(self):
        output_names = []
        for output in self.outputs:
            output_names.append(output.apsimOutputName)
        return output_names
    
    #
    # Extract the display output names from the array of output objects.
    #
    def get_display_output_names(self):
        output_names = []
        for output in self.outputs:
            if output.aggregateFunctions:
                for aggregate_function in output.aggregateFunctions:
                    output_names.append(aggregate_function.displayName)
            else:
                output_names.append(output.apsimOutputName)
        return output_names
        
    #
    # Determines if this is an environment typing run.
    #
    def get_is_environment_typing_run(self):
        return self.environmentTypes and len(self.environmentTypes) > 0

    
    #
    # Returns the type name.
    #
    def get_type_name(self):
        return __class__.__name__
