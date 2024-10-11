import lib.proto.path.proto_paths
import RelayApsim_pb2
import Types_pb2

from lib.proto.base.proto_request import ProtoRequest
from lib.proto.messages.run_apsim_response import RunApsimResponse

#
# A CGM Server request object that invokes APSIM runs, calling update parameters and passing in 
# the input values that will override the input traits that were sent in the InitWorkers request.
#
class RelayApsim(ProtoRequest):
    INPUT_START_INDEX = 0

    #
    # Constructor
    #
    def __init__(
        self, 
        job_id,
        individuals
    ):
        self.jobId = job_id
        self.individuals = individuals
        self.inputs = []
        self.simulationNames = []
        self.systemPropertyValues = []


    def get_unique_simulation_names(self):
        unique_simulation_names = list({name[1] for name in self.simulationNames})
        return unique_simulation_names

    #
    # Adds all of the input values, simulation names and system property values, for all of the env types.
    #
    def add_inputs_for_env_typing(self, environment_types, season_date_generator, variable_values_for_population):
        for input_id in range(0, len(variable_values_for_population)):

            input_values = variable_values_for_population[input_id]

            # Iterate over each environment type that was supplied.
            for simulation in environment_types:
                self.add_inputs_for_env_type(simulation, season_date_generator, input_id, input_values)


    #
    # Adds all of the input values, simulation names and system property values, for a specific env type.
    #
    def add_inputs_for_env_type(self, simulation, season_date_generator, input_id, input_values):
        for environment in simulation.Environments:
            for season in environment.Seasons:

                self.add_season(input_id, season_date_generator, season)
                self.add_simulation_name(input_id, simulation.Name)
                self.add_inputs_for_individual(input_id, input_values)

    #
    # Adds the season.
    #
    def add_season(self, input_id, season_date_generator, season):
        self.systemPropertyValues.append([
            str(input_id), 
            season_date_generator.generate_start_date_from_season(season), 
            season_date_generator.generate_end_date_from_season(season)
        ])

    #
    # Adds the simulation name.
    #
    def add_simulation_name(self, input_id, simulation_name):
        self.simulationNames.append([
            str(input_id), 
            simulation_name
        ])

    #
    # Adds all of the inputs.
    #
    def add_inputs(self, variable_values_for_population):
        for individual in range(RelayApsim.INPUT_START_INDEX, len(variable_values_for_population)):
            self.add_inputs_for_individual(individual, variable_values_for_population[individual])


    #
    # Adds all of the inputs.
    #
    def add_inputs_for_individual(self, individual, inputs):

        # Add the iteration id to the beginning of the array. 
        # We use the individual index for a convenient auto incrementing id.
        values = [individual]

        # Iterate over all of the input values that were passed in,
        # adding each one to the values array
        for input_value in inputs:
            values.append(input_value)

        # Now add the complete list of values which will contain the iteration
        # id, followed by all of the input values.
        self.inputs.append(values)


    def to_proto(self):
        relay_apsim_proto = RelayApsim_pb2.RelayApsimProto()
        relay_apsim_proto.JobID = self.jobId
        relay_apsim_proto.Individuals = self.individuals
       
       # Populate the Inputs field
        for input_list in self.inputs:
            double_array_proto = Types_pb2.DoubleArrayProto()
            double_array_proto.Values.extend(input_list)
            relay_apsim_proto.Inputs.append(double_array_proto)

        # Populate the SimulationNames field
        for sim_names in self.simulationNames:
            string_array_proto = Types_pb2.StringArrayProto()
            string_array_proto.Values.extend(sim_names)
            relay_apsim_proto.SimulationNames.append(string_array_proto)

        # Populate the SystemPropertyValues field
        for system_property_names in self.systemPropertyValues:
            string_array_proto = Types_pb2.StringArrayProto()
            string_array_proto.Values.extend(system_property_names)
            relay_apsim_proto.SystemPropertyValues.append(string_array_proto)

        return relay_apsim_proto


    @staticmethod
    def get_response_type() -> type:
        return RunApsimResponse


    @staticmethod
    def get_type_name():
        return __class__.__name__ + "Proto"