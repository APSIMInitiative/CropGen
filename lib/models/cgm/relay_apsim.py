import numpy as NumPy
import logging
import csv
import os.path

from os.path import exists
from lib.models.common.model import Model

#
# A WGP Server request object.
#
class RelayApsim(Model):
    INPUT_START_INDEX = 0
    #
    # Constructor
    #
    def __init__(self, run_job_request, generated_input_values):
        self.JobID = run_job_request.JobID
        self.Individuals = run_job_request.Individuals
        inputs_file = RelayApsim._get_inputs_file_path()

        if exists(inputs_file):
            self.Inputs = RelayApsim.create_input_values_from_file(
                generated_input_values,
                inputs_file, 
                run_job_request.Individuals,
                run_job_request.get_total_inputs()
            )
        else:
            self.Inputs = RelayApsim.create_input_values(generated_input_values)

    #
    # Returns the type name.
    #
    def get_type_name(self):
        return __class__.__name__
    
    #
    #
    #
    @staticmethod
    def _get_inputs_file_path():
        return os.path.join(os.path.dirname(__file__), "..", "..", "..", "inputs.csv")

    #
    #
    #
    @staticmethod
    def create_input_values_from_file(
        generated_input_values,
        inputs_file, 
        total_individuals,
        total_inputs
    ):
        input_values = []
        with open(inputs_file, "r") as f:
            reader = csv.reader(f, delimiter="\t")
            for line_number, line in enumerate(reader):
                if line_number > total_individuals: break

                if line_number == 0:
                    logging.info('Header line[{}] = {}'.format(line_number, line))
                else:
                    input_values.append(RelayApsim.HandleInputFileRow(generated_input_values, line_number, line, total_inputs))
        return input_values

    #
    #
    #
    @staticmethod
    def HandleInputFileRow(generated_input_values, line_number, line, total_inputs):
        logging.info('line[{}] = {}'.format(line_number, line))
        line_entries = line[0].split(',')
        values = [line_number - 1]
        for input_value in range(0, total_inputs):
            values.append(float(line_entries[input_value]))
        generated_input_values[line_number-1] = NumPy.array(values[1:])

        return values

    #
    # Creates input values, using the generated input values.
    #
    @staticmethod
    def create_input_values(generated_input_values):
        input_values = []
        for individual in range(RelayApsim.INPUT_START_INDEX, len(generated_input_values)):
            Inputs = generated_input_values[individual]

            # Add the iteration id to the beginning of the array. 
            # We use the individual index for a convenient auto incrementing id.
            values = [individual]

            # Iterate over all of the input values that were passed in,
            # adding each one to the values array
            for input_value in Inputs:
                values.append(input_value)

            # Now add the complete list of values which will contain the iteration
            # id, followed by all of the input values.
            input_values.append(values)

        return input_values
