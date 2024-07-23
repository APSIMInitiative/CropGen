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


    #
    # Adds all of the input values, simulation names and system property values, for all of the env types.
    #
    def add_inputs_for_env_typing(self, environment_types, season_date_generator, generated_input_values):
        for input_id in range(0, len(generated_input_values)):

            input_values = generated_input_values[input_id]

            # Iterate over each environment type that was supplied.
            for environment_type in environment_types:
                self.add_inputs_for_env_type(environment_type, season_date_generator, input_id, input_values)


    #
    # Adds all of the input values, simulation names and system property values, for a specific env type.
    #
    def add_inputs_for_env_type(self, environment_type, season_date_generator, input_id, input_values):
        for environment in environment_type.Environments:
            for season in environment.Seasons:
                start_date = season_date_generator.generate_start_date_from_season(season)
                end_date = season_date_generator.generate_end_date_from_season(season)

                self.systemPropertyValues.append([str(input_id), start_date, end_date])
                self.simulationNames.append([str(input_id), environment_type.Name])

                self.add_inputs_for_individual(input_id, input_values)
    

    #
    # Adds all of the inputs.
    #
    def add_inputs(self, generated_input_values):
        for individual in range(RelayApsim.INPUT_START_INDEX, len(generated_input_values)):
            self.add_inputs_for_individual(individual, generated_input_values[individual])


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
        for name in self.simulationNames:
            string_array_proto = Types_pb2.StringArrayProto()
            string_array_proto.Values.append(name)
            relay_apsim_proto.SimulationNames.append(string_array_proto)

        # Populate the SystemPropertyValues field
        for value in self.systemPropertyValues:
            string_array_proto = Types_pb2.StringArrayProto()
            string_array_proto.Values.append(value)
            relay_apsim_proto.SystemPropertyValues.append(string_array_proto)

        return relay_apsim_proto


    @staticmethod
    def get_response_type() -> type:
        return RunApsimResponse


    def get_type_name(self):
        return __class__.__name__ + "Proto"