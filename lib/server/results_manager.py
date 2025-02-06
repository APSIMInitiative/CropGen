from pathlib import Path
import shutil
import zipfile
import csv

class ResultsManager:
    def __init__(self, config, server_state, crop_gen_job, version_info):
        self.config = config
        self.server_state = server_state
        self.crop_gen_job = crop_gen_job
        self.version_info = version_info

        self.results_dir = Path(config.results_dir)
        self.job_results_dir = self.results_dir / crop_gen_job.jobId

        self.job_file = self.job_results_dir / "cropgen_job.json"
        self.progress_file = self.job_results_dir / "progress.txt"
        self.all_individuals_path = self.job_results_dir / "all_individuals.csv"
        self.optimal_individuals_path = self.job_results_dir / "optimal_individuals.csv"
        self.version_info_path = self.job_results_dir / "version_info.txt"
        self.zip_file_dir = self.results_dir / f"{crop_gen_job.jobId}.zip"

        self.create_results_dir()


    def create_results_dir(self):
        if self.job_results_dir.exists():
            shutil.rmtree(self.job_results_dir)

        self.job_results_dir.mkdir(parents=True, exist_ok=True)

        self.write_job_file_to_results()
        self.write_version_info_to_results()
        self.create_csv_files()


    def write_iteration_result(self, iteration_result, avg_run_time):
        if iteration_result.iterationID == 1:
            self._write_header_row(self.all_individuals_path, iteration_result)

        self._write_individuals(self.all_individuals_path, iteration_result, lambda result: self.crop_gen_job.individuals)

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
        self.progress_file.write_text(progress_str + '\n', append=True)


    def zip_results(self):
        self.copy_logs_to_results()

        # Delete existing zip file
        self.zip_file_dir.unlink(missing_ok=True)

        # Create zip file and add contents of job_results_dir
        with zipfile.ZipFile(self.zip_file_dir, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in self.job_results_dir.rglob('*'):
                zipf.write(file, file.relative_to(self.job_results_dir))

        self.remove_results_dir()
        return self.zip_file_dir


    def _write_header_row(self, file_path, result):
        headers = [input.name for input in result.inputs] + [output.name for output in result.outputs]
        with file_path.open('a', newline='') as file:
            csv.writer(file).writerow(headers)


    def _write_individuals(self, file_path, result, get_individual_count):
        with file_path.open('a', newline='') as file:
            writer = csv.writer(file)
            for i in range(get_individual_count(result)):
                row = [input.values[i] for input in result.inputs] + [output.values[i] for output in result.outputs]
                writer.writerow(row)


    def copy_logs_to_results(self):
        if not self.config.CopyLogsToResults:
            return

        log_destination = self.job_results_dir / 'logs'
        shutil.rmtree(log_destination, ignore_errors=True)
        shutil.copytree(self.config.log_dir, log_destination)


    def write_version_info_to_results(self):
        if not self.config.WriteVersionInfoToResults:
            return

        self.version_info_path.write_text(self.version_info.to_string())


    def write_job_file_to_results(self):
        self.job_file.write_text(self.crop_gen_job.to_json(True))


    def create_csv_files(self):
        for path in [self.all_individuals_path, self.optimal_individuals_path, self.progress_file]:
            path.touch()


    def remove_results_dir(self):
        if not self.zip_file_dir.exists() or not self.config.delete_results_dir_after_zip:
            return

        shutil.rmtree(self.job_results_dir, ignore_errors=True)
