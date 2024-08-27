import os
import shutil
import zipfile
import csv

class ResultsManager:
    def __init__(self, config, server_state, crop_gen_job):
        self.config = config
        self.server_state = server_state
        self.crop_gen_job = crop_gen_job
        self.progress_file = ""
        self.all_individuals_path = ""
        self.optimal_individuals_path = ""
        self.zip_file_dir = ""
        self.results_dir = ""
        self.job_results_dir = ""

        self.create_results_dir()


    def create_results_dir(self):
        self.results_dir = self.config.results_dir
        self.job_results_dir = os.path.join(self.results_dir, self.crop_gen_job.jobId)

        if os.path.exists(self.job_results_dir):
            shutil.rmtree(self.job_results_dir)

        os.makedirs(self.job_results_dir, exist_ok=True)

        self.progress_file = os.path.join(self.job_results_dir, "progress.txt")
        self.all_individuals_path = os.path.join(self.job_results_dir, "all_individuals.csv")
        self.optimal_individuals_path = os.path.join(self.job_results_dir, "optimal_individuals.csv")
        self.zip_file_dir = os.path.join(self.results_dir, f"{self.crop_gen_job.jobId}.zip")

        open(self.all_individuals_path, 'w').close()
        open(self.optimal_individuals_path, 'w').close()
        open(self.progress_file, 'w').close()


    def write_iteration_result(self, iteration_result, avg_run_time):
        if iteration_result.iterationID == 1:
            self._write_header_row(self.all_individuals_path, iteration_result)

        self._write_individuals(
            self.all_individuals_path,
            iteration_result,
            lambda result: self.crop_gen_job.individuals
        )

        self.write_progress(iteration_result.to_progress_str())
        self.server_state.set_iteration_complete(iteration_result.iterationID, avg_run_time)


    def write_final_result(self, final_result):
        self._write_header_row(self.optimal_individuals_path, final_result)

        self._write_individuals(
            self.optimal_individuals_path,
            final_result,
            lambda result: min(len(result.inputs[0].values), len(result.outputs[0].values))
        )

        self.write_progress(final_result.to_progress_str())
        self.server_state.set_job_complete()


    def write_progress(self, progress_str):
        progress_str_with_newline = progress_str + '\n'
        with open(self.progress_file, 'a') as f:
            f.write(progress_str_with_newline)


    def zip_results(self):
        self.copy_logs_to_results()
        
        # Delete results zip file if it already exists.
        if os.path.exists(self.zip_file_dir): os.remove(self.zip_file_dir)

        # Create a zip file and add the contents of result_dir
        with zipfile.ZipFile(self.zip_file_dir, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.job_results_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=self.job_results_dir)
                    zipf.write(file_path, arcname)

        self.remove_results_dir()

        return self.zip_file_dir
    

    def _write_header_row(self, file_path, result):
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)

            header_row = []

            for input in result.inputs:
                header_row.append(input.name)
            for output in result.outputs:
                header_row.append(output.name)

            writer.writerow(header_row)


    def _write_individuals(self, file_path, result, get_individual_count):
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)

            for individual in range(get_individual_count(result)):
                row = []

                for input in result.inputs:
                    input_value = input.values[individual]
                    row.append(input_value)

                for output in result.outputs:
                    output_value = output.values[individual]
                    row.append(output_value)

                writer.writerow(row)


    def create_results_zip_file(self):
        self.copy_logs_to_results()
        
        # Delete results zip file if it already exists.
        if os.path.exists(self.zip_file_dir): os.remove(self.zip_file_dir)

        # Create a zip file and add the contents of result_dir
        with zipfile.ZipFile(self.zip_file_dir, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.job_results_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=self.job_results_dir)
                    zipf.write(file_path, arcname)

        self.remove_results_dir()


    def copy_logs_to_results(self):
        if not self.config.CopyLogsToResults: return

        log_destination_dir_path = os.path.join(self.job_results_dir, 'logs')
        if os.path.exists(log_destination_dir_path): shutil.rmtree(log_destination_dir_path) 
        shutil.copytree(self.config.log_dir, log_destination_dir_path)


    def remove_results_dir(self):
        if not os.path.exists(self.zip_file_dir): return
        if not self.config.DeleteResultsDirAfterZip: return

        if os.path.exists(self.job_results_dir):
            shutil.rmtree(self.job_results_dir)
