import unittest
import random
from test.test_base import TestBase
from test.helpers.cropgen_job_helper import CropGenJobHelper
from lib.proto.messages.apsim_result import ApsimResult
from lib.aggregate_functions.weighted_mean_function import WeightedMeanFunction

class WeightedMeanFunctionTests(TestBase):

    def generate_apsim_results(self, num_results, value_range=(100, 1000), text_values=None):
        if text_values is None:
            text_values = ["15-nov", "Dalby_GC150M_Current"]
        
        apsim_results = []
        for _ in range(num_results):
            apsim_result = ApsimResult()
            value = random.uniform(*value_range)
            apsim_result.values.append(value)
            apsim_result.text_values.append(random.choice(text_values))
            apsim_results.append(apsim_result)
        return apsim_results


    def test_calculate(self):
        # Arrange
        apsim_results = []
        apsim_results.extend(self.generate_apsim_results(5, value_range=(800, 900), text_values=["15-nov", "Dalby_GC150M_Current"]))
        apsim_results.extend(self.generate_apsim_results(5, value_range=(100, 200), text_values=["15-nov", "Emerald_GC150M_Current"]))

        cropgen_job_helper = CropGenJobHelper("weighted.json")
        cropgen_job = cropgen_job_helper.parse()
        weighted_mean_aggregate_function = cropgen_job.outputs[0].aggregateFunctions[0]

        # Act
        actual = WeightedMeanFunction.calculate(cropgen_job, weighted_mean_aggregate_function, apsim_results, 0)

        # Assert
        # You can implement the expected value and assert it if you have a known expected value
        # self.assertEqual(actual, expected, f"Expected: {expected}, but got: {actual}")

if __name__ == "__main__":
    unittest.main()
