import unittest

from parameterized import parameterized
from test.test_base import TestBase
from test.helpers.apsim_result_helper import ApsimResultHelper
from lib.aggregate_functions.mean_function import MeanFunction

class MeanFunctionTests(TestBase):

    @parameterized.expand([
        ([10, 10, 10, 10, 10], 0, 10),
        ([100, 0, 0, 0, 0], 0, 20),
        ([100], 0, 100),
        ([100, 20], 0, 60),
        ([], 0, 0)
    ])
    def test_calculate(self, result_values, apsim_output_index, expected):
        # Arrange
        results_for_individual = ApsimResultHelper.create_results_for_individual(
            result_values, [], apsim_output_index
        )

        # Act
        actual = MeanFunction.calculate(results_for_individual, apsim_output_index)

        # Assert
        self.assertEqual(actual, expected, f"result_values: {result_values} apsim_output_index: {apsim_output_index} expected: {expected} actual: {actual}")

if __name__ == "__main__":
    unittest.main()
