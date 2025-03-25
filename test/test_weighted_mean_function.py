import unittest

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
        evapotranspiration_output_value = 999
        apsim_results = [
            self.generate_apsim_result([500, evapotranspiration_output_value], ["15-aug", "Dalby_GC150M_Current"]),
            self.generate_apsim_result([520, evapotranspiration_output_value], ["15-aug", "Dalby_Extra"]),

            self.generate_apsim_result([600, evapotranspiration_output_value], ["15-sep", "Dalby_"]),
            self.generate_apsim_result([620, evapotranspiration_output_value], ["15-sep", "Dalby_"]),
            self.generate_apsim_result([640, evapotranspiration_output_value], ["15-sep", "Dalby_"]),

            self.generate_apsim_result([700, evapotranspiration_output_value], ["15-oct", "Dalby_"]),
            self.generate_apsim_result([710, evapotranspiration_output_value], ["15-oct", "Dalby_"]),
            self.generate_apsim_result([730, evapotranspiration_output_value], ["15-oct", "Dalby_"]),

            self.generate_apsim_result([800, evapotranspiration_output_value], ["15-nov", "Dalby_"]),
            self.generate_apsim_result([820, evapotranspiration_output_value], ["15-nov", "Dalby_"]),
            self.generate_apsim_result([850, evapotranspiration_output_value], ["15-nov", "Dalby_"]),

            # Emerald: Multiple entries for each sowing date
            self.generate_apsim_result([100, evapotranspiration_output_value], ["15-aug", "Emerald_GC150M_Current"]),
            self.generate_apsim_result([120, evapotranspiration_output_value], ["15-aug", "Emerald_Extra"]),

            self.generate_apsim_result([200, evapotranspiration_output_value], ["15-sep", "Emerald_"]),
            self.generate_apsim_result([210, evapotranspiration_output_value], ["15-sep", "Emerald_"]),
            self.generate_apsim_result([230, evapotranspiration_output_value], ["15-sep", "Emerald_"]),

            self.generate_apsim_result([300, evapotranspiration_output_value], ["15-oct", "Emerald_"]),
            self.generate_apsim_result([310, evapotranspiration_output_value], ["15-oct", "Emerald_"]),
            self.generate_apsim_result([330, evapotranspiration_output_value], ["15-oct", "Emerald_"]),

            self.generate_apsim_result([400, evapotranspiration_output_value], ["15-nov", "Emerald_"]),
            self.generate_apsim_result([420, evapotranspiration_output_value], ["15-nov", "Emerald_"]),
            self.generate_apsim_result([450, evapotranspiration_output_value], ["15-nov", "Emerald_"])
        ]

        cropgen_job_helper = CropGenJobHelper("weighted.json")
        cropgen_job = cropgen_job_helper.parse()
        weighted_mean_aggregate_function = cropgen_job.outputs[0].aggregateFunctions[0]

        # Act
        actual = WeightedMeanFunction.calculate(cropgen_job, weighted_mean_aggregate_function, apsim_results, 0)

        # Assert: Ensure the result is not None
        self.assertIsNotNone(actual, "The calculated yield should not be None.")

        # Assert: Ensure the result is a number
        self.assertIsInstance(actual, (float), f"Yield {actual} should be numeric.")

        # Assert: Ensure the yield is positive
        self.assertGreater(actual, 0, "The calculated proportional yield should be greater than zero.")


if __name__ == "__main__":
    unittest.main()
