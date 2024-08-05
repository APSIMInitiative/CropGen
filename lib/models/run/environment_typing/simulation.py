from lib.models.common.model import Model
from lib.utils.json_helper import JsonHelper
from lib.models.run.environment_typing.environment_data import EnvironmentData

#
# Represents a simulation within an environment type.
#
class Simulation(Model):
    #
    # Constructor
    #
    def __init__(self, name, environments):
        self.Name = name
        self.Environments = environments

    #
    # Parses the environment types
    #
    @staticmethod
    def parse(json_object, errors):
        name = JsonHelper.get_attribute(json_object, 'name', '', True)
        environments = JsonHelper.get_attribute(json_object, 'environments', [], True)

        parsed_environments = []
        for environment in environments:
            parsed_environments.append(EnvironmentData.parse(environment, errors))

        return Simulation(name, parsed_environments)

    #
    # Returns the type name.
    #
    @staticmethod
    def get_type_name():
        return __class__.__name__