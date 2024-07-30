from lib.models.common.model import Model

#
# Represents an input or an output
#
class InputOutput(Model):
    #
    # Constructor
    #
    def __init__(
        self, 
        name, 
        values, 
        simulation_id=None, 
        simulation_name=None
    ):
        self.name = name
        self.values = values
        self.simulationId = simulation_id
        self.simulationName = simulation_name
    
    #
    # Creates a progress string based on this data.
    #
    def to_progress_str(self):
        progress_str = (
            f"Name: {self.name}\n"
            f"Values: [{', '.join(str(v) for v in self.values)}]"
        )

        if self.simulationId is not None:
            progress_str += f"\nSimulation ID: {self.simulationId}"

        if self.simulationName is not None:
            progress_str += f"\nSimulation Name: {self.simulationName}"
        
        return progress_str