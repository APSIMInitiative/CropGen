import os
import csv

class ResultsManager:
    def __init__(self):
        self.input_names = []
        self.output_names = []
        self.individuals = 0
        self.iteration_results = []
        self.final_result = None


    def add_iteration_result(self, result):
        self.iteration_results.append(result)


    def set_input_output_names(self, crop_gen_job):
        self.input_names = crop_gen_job.get_input_names()
        self.output_names = crop_gen_job.get_display_output_names()
        self.individuals = crop_gen_job.individuals


    def add_final_result(self, result):
        if self.final_result is None:
            self.final_result = result
        else:
            raise ValueError("Final result has already been set.")


    def clear(self):
        self.iteration_results.clear()
        self.final_result = None


    def write_to_disk(self, dir):
        os.makedirs(dir, exist_ok=True)

        self.write_all_individuals(dir)


    def write_all_individuals(self, dir):
        all_individuals_path = os.path.join(dir, "all_individuals.csv")
        with open(all_individuals_path, mode='w', newline='') as file:
            
            writer = csv.writer(file)

            header = self.input_names + self.output_names
            writer.writerow(header)

            for result in self.iteration_results:
                for individual in range(self.individuals):
                    row = []

                    for input in result.inputs:
                        input_value = input.values[individual]
                        row.append(input_value)

                    for output in result.outputs:
                        output_value = output.values[individual]
                        row.append(output_value)

                    writer.writerow(row)