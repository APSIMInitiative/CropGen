class OutputValue():
    #
    # Constructor
    #
    def __init__(
        self, 
        raw_apsim_output, 
        output_name,
        output_maximise,
        output_multiplier
    ):
        self.raw_apsim_output = raw_apsim_output
        self.output_name = output_name
        self.output_maximise = output_maximise
        self.output_multiplier = output_multiplier

    #
    # Gets the name of the output.
    #
    def get_output_name(self):
        return self.output_name

    #
    # Gets the output value for use in the minimise algorithm.
    #
    def get_output_value_for_algorithm(self):
        if self.output_maximise:
            return -abs(self.raw_apsim_output)
        return self.raw_apsim_output
    
    #
    # Gets the output value from the algorithm.
    #
    def get_output_value_from_algorithm(self):
        result = self.raw_apsim_output
        if self.output_maximise:
            result = abs(self.raw_apsim_output)
        
        if self.output_multiplier > 0:
            result *= self.output_multiplier

        return result
    
    #
    # Gets the output value for use in results.
    #
    def get_output_value_for_results(self):
        result = self.raw_apsim_output

        if self.output_multiplier > 0:
            result *= self.output_multiplier
        return result