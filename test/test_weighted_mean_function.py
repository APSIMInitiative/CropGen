import unittest
import random

from test.test_base import TestBase
from test.helpers.cropgen_job_helper import CropGenJobHelper
from lib.proto.messages.apsim_result import ApsimResult
from lib.aggregate_functions.weighted_mean_function import WeightedMeanFunction

class WeightedMeanFunctionTests(TestBase):

    def generate_apsim_result(self, output_values, text_values):
        apsim_result = ApsimResult()
        apsim_result.values = output_values
        apsim_result.text_values = text_values
        return apsim_result

    def test_calculate(self):
        # Arrange
        dalby_aug_weight = None
        dalby_sep_weight = 0.55
        dalby_oct_weight = 0.91
        dalby_nov_weight = 1.11

        emerald_aug_weight = None
        emerald_sep_weight = 0.5
        emerald_oct_weight = 0.95
        emerald_nov_weight = 1.10

        # Outputs are Yield and Evapotranspiration (as per weighted.json file)
        apsim_results = [
            self.generate_apsim_result([500, 0], ["15-aug", "Dalby_GC150M_Current"]),
            self.generate_apsim_result([600, 0], ["15-sep", "Dalby_"]),
            self.generate_apsim_result([700, 0], ["15-oct", "Dalby_"]),
            self.generate_apsim_result([800, 0], ["15-nov", "Dalby_kjkjkjkjkjkjkjk"]),

            self.generate_apsim_result([100, 0], ["15-aug", "Emerald_GC150M_Current"]),
            self.generate_apsim_result([200, 0], ["15-sep", "Emerald_"]),
            self.generate_apsim_result([300, 0], ["15-oct", "Emerald_"]),
            self.generate_apsim_result([400, 0], ["15-nov", "Emerald_kjkjkjkjkjkjkjk"])
        ]

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
