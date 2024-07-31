from enum import IntEnum

from lib.models.common.model import Model
from lib.models.run.aggregate_function import AggregateFunction
from lib.utils.json_helper import JsonHelper

#
# Represents an output that is sent as part of a run job request.
#
class Output(Model):
    #
    # Constructor
    #
    def __init__(self, apsim_output_name, optimise, maximise, multiplier, aggregate_functions):
        self.apsimOutputName = apsim_output_name
        self.optimise = optimise
        self.maximise = maximise
        self.multiplier = multiplier
        self.aggregateFunctions = aggregate_functions

    #
    # Parses the outputs
    #
    @staticmethod
    def parse_from_json_object(lower_case_json_data, errors):
        outputs = JsonHelper.get_attribute(lower_case_json_data, 'outputs', errors)

        if not outputs:
            errors.append("No outputs supplied.")
            return []

        total_outputs_to_optimise = 0
        parsed_outputs = []
        for output_value in outputs:
            apsim_output_name = JsonHelper.get_attribute(output_value, 'apsimOutputName', errors)
            optimise = JsonHelper.get_non_mandatory_attribute(output_value, 'optimise', True)
            maximise = JsonHelper.get_non_mandatory_attribute(output_value, 'maximise', False)
            multiplier = JsonHelper.get_non_mandatory_attribute(output_value, 'multiplier', 1)
            aggregate_functions = AggregateFunction.parse_aggregate_functions(output_value, errors)

            parsed_outputs.append(Output(
                apsim_output_name, optimise, maximise, multiplier, aggregate_functions
            ))

            # Keep track of the items that should be optimised.
            if optimise: 
                total_outputs_to_optimise +=1

        # Final check to ensure that we have at least one output to optimise
        if not total_outputs_to_optimise:
            errors.append(f"No outputs have been configured to optimise. Total outputs: '{len(parsed_outputs)}'")
            return []
            
        return parsed_outputs

    #
    # Returns the type name.
    #
    def get_type_name(self):
        return __class__.__name__