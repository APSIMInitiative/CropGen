import unittest
import random
import pandas as pd
import numpy as np
import os
import csv
import inspect

from test.test_base import TestBase
from test.helpers.cropgen_job_helper import CropGenJobHelper
from test.helpers.cropgen_csv_helper import CropGenCsvHelper
from lib.aggregate_functions.weighted_mean_function import WeightedMeanFunction
from lib.aggregate_functions.aggregated_data_state import AggregatedDataState

class WeightedFunctionCompareTests(TestBase):

    def test_calculate(self):
        # Arrange        
        cropgen_job = CropGenJobHelper("weighted_dalby.json").parse()        
        weighted_mean_aggregate_function = cropgen_job.outputs[0].aggregateFunctions[0]
        apsim_results = CropGenCsvHelper("dalby.csv").parse()
        output_index = 0
        apsim_results_df = self.convert_apsim_results_to_dataframe(apsim_results, output_index)
        algorithm_results = []
        prototype_results = []
        sample_size = 1000

        # Act
        for _ in range(sample_size):
            algorithm_results.append(WeightedMeanFunction.calculate(
                cropgen_job, 
                weighted_mean_aggregate_function, 
                apsim_results, 
                output_index,
                # This is important to pass an empty AggregatedDataState as it caches the results which we don't want to do in this test
                AggregatedDataState()
            ))

            prototype_results.append(self.calculate_mean_prototype(cropgen_job, apsim_results_df))


        # Write results to CSV for comparison
        self.write_results_csv(algorithm_results, prototype_results)
        
        # Assert
        assert len(algorithm_results) == sample_size
        assert len(prototype_results) == sample_size
        algo_total = sum(algorithm_results)
        prototype_total = sum(prototype_results)

        # Compare totals within a tolerance
        tolerance = 300
        assert abs(algo_total - prototype_total) <= tolerance, (
            f"Totals do not match: algo_total={algo_total}, prototype_total={prototype_total}, "
            f"diff={abs(algo_total - prototype_total)} > tolerance={tolerance}"
        )


    def calculate_mean_prototype(
        self,
        cropgen_job,
        apsim_results_df
    ):
        proportional_yields = []

        for site in cropgen_job.sowingDateWeighting:
            site_data = cropgen_job.sowingDateWeighting[site]

            for sowing_date, weight in site_data.weights.items():
                if weight is not None:
                    df = apsim_results_df[apsim_results_df['SowingDate']== sowing_date]
                    sowing_yields = list(df['Yield'])
                    num = round(len(sowing_yields) * weight)
                    prop_sowing_yields = random.choices(sowing_yields, k=num)
                    proportional_yields.extend(prop_sowing_yields)

        
        result = np.average(proportional_yields)
        return result


    def convert_apsim_results_to_dataframe(self, apsim_results, output_index):
        all_rows = []
        for result in apsim_results:
            all_rows.append({
                'Yield': result.values[output_index],
                'SowingDate': result.text_values[0],
                'Site': result.text_values[1]
            })
        return pd.DataFrame(all_rows)


    def write_results_csv(self, algorithm_results, prototype_results, filename="results_output.csv"):
        # Get path to current file
        current_file_path = inspect.getfile(inspect.currentframe())
        current_dir = os.path.dirname(os.path.abspath(current_file_path))
        output_path = os.path.join(current_dir, filename)

        # Write to CSV
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["AlgorithmResults", "PrototypeResults"])

            # Ensure equal length
            max_len = max(len(algorithm_results), len(prototype_results))
            padded_algo = algorithm_results + ["" for _ in range(max_len - len(algorithm_results))]
            padded_proto = prototype_results + ["" for _ in range(max_len - len(prototype_results))]

            for row in zip(padded_algo, padded_proto):
                writer.writerow(row)


if __name__ == "__main__":
    unittest.main()
