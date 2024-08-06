import os
import shutil
import zipfile
import csv

from lib.utils.date_time_helper import DateTimeHelper

class ResultsManager:
    def __init__(self, config, jobs_server, crop_gen_job):
        self.config = config
        self.jobs_server = jobs_server
        self.crop_gen_job = crop_gen_job
        self.iteration_results = []
        self.final_result = None
        self.result_dir = self.create_results_dir()
        self.zip_file_dir = self.create_results_zip_file_path()
        self.progress_file = os.path.join(self.result_dir, "progress.txt")


    def create_results_dir(self):
        results_dir = os.path.join(
            self.config.results_dir, 
            self.crop_gen_job.jobId,
            DateTimeHelper.get_date_time_now_str_dir_format()
        )

        os.makedirs(results_dir, exist_ok=True)

        return results_dir
    

    def create_results_zip_file_path(self):
        return os.path.join(
            self.config.results_dir, 
            f"{self.crop_gen_job.jobId}.zip"
        )


    def add_iteration_result(self, iteration_result, avg_run_time):
        self.iteration_results.append(iteration_result)
        progress_str = iteration_result.to_progress_str()
        self.write_progress(progress_str)
        self.jobs_server.set_iteration_complete(iteration_result.iterationID, avg_run_time)


    def add_final_result(self, final_result):
        if self.final_result is None:
            self.final_result = final_result
            progress_str = final_result.to_progress_str()
            self.write_progress(progress_str)
            self.jobs_server.set_job_complete()
        else:
            raise ValueError("Final result has already been set.")
        

    def write_progress(self, progress_str):
        progress_str_with_newline = progress_str + '\n'
        if not os.path.exists(self.progress_file):
            with open(self.progress_file, 'w') as f:
                f.write(progress_str_with_newline)
        else:
            with open(self.progress_file, 'a') as f:
                f.write(progress_str_with_newline)


    def clear(self):
        self.iteration_results.clear()
        self.final_result = None


    def write_to_disk(self):
        os.makedirs(self.result_dir, exist_ok=True)

        self.write_all_individuals()
        self.write_optimal_individuals()
        self.create_results_zip_file()
        self.clear()
        return self.zip_file_dir


    def _write_individuals(self, file_path, results, get_individual_count):
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            first_row = True

            for result in results:
                for individual in range(get_individual_count(result)):
                    header_row = []
                    row = []

                    for input in result.inputs:
                        header_row.append(input.name)
                        input_value = input.values[individual]
                        row.append(input_value)

                    for output in result.outputs:
                        header_row.append(output.name)
                        output_value = output.values[individual]
                        row.append(output_value)

                    if first_row:
                        writer.writerow(header_row)
                        first_row = False

                    writer.writerow(row)


    def write_all_individuals(self):
        all_individuals_path = os.path.join(self.result_dir, "all_individuals.csv")
        self._write_individuals(
            all_individuals_path,
            self.iteration_results,
            lambda result: self.crop_gen_job.individuals
        )
        

    def write_optimal_individuals(self):
        optimal_individuals_path = os.path.join(self.result_dir, "optimal_individuals.csv")
        self._write_individuals(
            optimal_individuals_path,
            [self.final_result],
            lambda result: min(len(result.inputs[0].values), len(result.outputs[0].values))
        )


    def create_results_zip_file(self):
        self.copy_logs_to_results()
        
        # Delete results zip file if it already exists.
        if os.path.exists(self.zip_file_dir): os.remove(self.zip_file_dir)

        # Create a zip file and add the contents of result_dir
        with zipfile.ZipFile(self.zip_file_dir, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.result_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=self.result_dir)
                    zipf.write(file_path, arcname)


    def copy_logs_to_results(self):
        if not self.config.CopyLogsToResults: return

        log_destination_dir_path = os.path.join(self.result_dir, 'logs')
        if os.path.exists(log_destination_dir_path): shutil.rmtree(log_destination_dir_path) 
        shutil.copytree(self.config.log_dir, log_destination_dir_path)
