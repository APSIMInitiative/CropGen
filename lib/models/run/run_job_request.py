import json

from lib.models.common.model import Model
from lib.models.run.input import Input
from lib.models.run.output import Output
from lib.models.run.environment_typing.simulation import Simulation
from lib.utils.json_helper import JsonHelper
from lib.config.apsim_simulation_data import APSimSimulationData

#
# Model that represents a run job request sent from the jobs server
#
class RunJobRequest(Model):
    #
    # Constructor.
    #
    def __init__(self):
        self.JobID = ''
        self.CGMServerHost = ''
        self.CGMServerPort = 0
        self.IterationResultsUrl = ''
        self.FinalResultsUrl = ''
        self.ApsimUrl = ''
        self.Iterations = 0
        self.Individuals = 0
        self.Seed = 1
        self.ReportName = ''
        self.Inputs = []
        self.Outputs = []
        self.EnvironmentTypes = []
        self.APSIMSimulationClockStartDate = ''
        self.MaxSimulationsPerRequest = None

    #
    # Parses the JSON data into this class.
    #
    def parse_from_json_string(self, message):
        errors = []

        try:
            json_object = json.loads(message)
            self.JobID = JsonHelper.get_attribute(json_object, 'JobID', errors)
            self.CGMServerHost = JsonHelper.get_attribute(json_object, 'CGMServerHost', errors)
            self.CGMServerPort = JsonHelper.get_attribute(json_object, 'CGMServerPort', errors)
            self.IterationResultsUrl = JsonHelper.get_attribute(json_object, 'IterationResultsUrl', errors)
            self.FinalResultsUrl = JsonHelper.get_attribute(json_object, 'FinalResultsUrl', errors)
            self.ApsimUrl = JsonHelper.get_attribute(json_object, 'ApsimUrl', errors)
            self.Iterations = JsonHelper.get_attribute(json_object, 'Iterations', errors)
            self.Individuals = JsonHelper.get_attribute(json_object, 'Individuals', errors)
            self.Seed = JsonHelper.get_non_mandatory_attribute(json_object, 'Seed', None)
            self.ReportName = JsonHelper.get_attribute(json_object, 'ReportName', errors)
            self.Inputs = Input.parse_inputs(json_object, errors)
            self.Outputs = Output.parse_outputs(json_object, errors)
            self.EnvironmentTypes = RunJobRequest.parse_environment_types(json_object, errors)
            self.APSIMSimulationClockStartDate = JsonHelper.get_non_mandatory_attribute(json_object, 'APSIMSimulationClockStartDate', None)
            self.MaxSimulationsPerRequest = JsonHelper.get_non_mandatory_attribute(json_object, 'MaxSimulationsPerRequest', None)
        except Exception as error:
            errors.append(f"Failed to parse {self.get_type_name()} JSON: '{message}'. Error: '{error}'")

        return errors
    
    #
    # Helper function to parse the environment types.
    #
    @staticmethod
    def parse_environment_types(json_object, errors):
        environment_types = JsonHelper.get_non_mandatory_attribute(json_object, 'EnvironmentTypes', [])

        if not environment_types: return []
        
        parsed_env_types = []

        for environment_type_value in environment_types:
            simulation = JsonHelper.get_attribute(environment_type_value, 'Simulation', errors)
            parsed_env_types.append(Simulation.parse(simulation, errors))
            
        return parsed_env_types

    #
    # Simple helper for getting the total number of Inputs defined
    #
    def get_total_inputs(self):
        return len(self.Inputs)

    #
    # Simple helper for getting the total number of outputs defined
    #
    def get_total_outputs(self):
        total_outputs = 0
        for output in self.Outputs:
            total_aggregate_functions = len(output.AggregateFunctions)
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
        for output in self.Outputs:
            if output.Optimise:
                total_aggregate_functions = len(output.AggregateFunctions)
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
        if len(self.Outputs) > index:
            return self.Outputs[index]
        return output
    
    #
    # Extract the input names from the array of input objects.
    #
    def get_input_names(self):
        input_names = []
        for input in self.Inputs:
            input_names.append(input.Name)
        return input_names
    
    #
    # Extract the APSIM output names from the array of output objects.
    #
    def get_apsim_output_names(self):
        output_names = []
        for output in self.Outputs:
            output_names.append(output.ApsimOutputName)
        return output_names
    
    #
    # Extract the display output names from the array of output objects.
    #
    def get_display_output_names(self):
        output_names = []
        for output in self.Outputs:
            if output.AggregateFunctions:
                for aggregate_function in output.AggregateFunctions:
                    output_names.append(aggregate_function.DisplayName)
            else:
                output_names.append(output.ApsimOutputName)
        return output_names
    
    #
    # Gets the list of simulations to be ran.
    #
    def get_simulations_and_seasons_to_run(self):
        simulations = {}
        for env_type in self.EnvironmentTypes:
            simulation_name = env_type.Name
            season = env_type.Season
            if simulation_name in simulations:
                simulations[simulation_name].append(season)
            else:
                simulations[simulation_name] = [season]
        return simulations
    
    #
    # Gets the list of simulations to be ran.
    #
    def get_simulations_to_run(self):
        if self.get_is_environment_typing_run():
            simulations = []
            for env_type in self.EnvironmentTypes:
                simulation_name = env_type.Name
                if simulation_name not in simulations:
                    simulations.append(simulation_name)
            return simulations
        
        elif self.MaxSimulationsPerRequest:
            apsim_data = APSimSimulationData()
            simulation_names = apsim_data.get_simulation_names(self.JobID)
            if simulation_names: return simulation_names

        return []
    
    #
    # Determines whether the APSIM runner should be reset each Relay Apsim request or whether it should
    # use a fixed runner all of the way through the job.
    #
    def get_should_reset_runner(self, config):

        if config.AlwaysResetRunner:
            return True

        reset_runner = (
            self.get_is_environment_typing_run() or 
            (
                self.MaxSimulationsPerRequest is not None and 
                self.MaxSimulationsPerRequest != 0
            )
        )

        return reset_runner
    
    #
    # Get a collection of system property names that we want to override.
    #
    def get_system_property_names(self, config):
        if not self.get_is_environment_typing_run():
            return []
        
        # If we have some environment types then we want to manipulate the clock start and end date (year only)
        # so that we can run specific simulations, for specific years.
        return [
            config.ApsimClockStartDateYearInputName,
            config.ApsimClockEndDateYearInputName
        ]

    #
    # Determines if this is an environment typing run.
    #
    def get_is_environment_typing_run(self):
        return self.EnvironmentTypes and len(self.EnvironmentTypes) > 0
    
    #
    # Returns the type name.
    #
    def get_type_name(self):
        return __class__.__name__
