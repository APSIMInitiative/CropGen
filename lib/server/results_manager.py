import csv

class ResultsManager:
    def __init__(self):
        self.iteration_results = []
        self.final_result = None


    def add_iteration_result(self, result):
        self.iteration_results.append(result)


    def add_final_result(self, result):
        if self.final_result is None:
            self.final_result = result
        else:
            raise ValueError("Final result has already been set.")


    def clear(self):
        self.iteration_results.clear()
        self.final_result = None


    def write_to_disk(self, file_path):
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Write headers
            writer.writerow(['Type', 'Result'])
            
            # Write iteration results
            for result in self.iteration_results:
                writer.writerow(['Iteration', result])
            
            # Write final result
            if self.final_result is not None:
                writer.writerow(['Final', self.final_result])
            else:
                writer.writerow(['Final', 'No final result'])