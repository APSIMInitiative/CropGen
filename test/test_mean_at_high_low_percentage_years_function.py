import unittest

from parameterized import parameterized
from test.test_base import TestBase
from test.helpers.test_aggregate_function import TestAggregateFunction
from test.helpers.apsim_result_helper import ApsimResultHelper
from lib.aggregate_functions.mean_at_high_low_percentage_years_function import MeanAtHighLowPercentageYears

class MeanFunctionTests(TestBase):

    @parameterized.expand([
        ("highest", "20", 0, 154.48, True),
        ("highest", "20", 0, 155.04, False),
        ("highest", "10", 0, 162.50, True),
        ("highest", "10", 0, 162.50, False),
        ("lowest",  "20", 0, 13.36, True),
        ("lowest",  "20", 0, 12.79, False),
        ("lowest",  "10", 0, 6.33, True),
        ("lowest",  "10", 0, 6.33, False),
    ])
    def test_calculate(self, high_low, percentage, apsim_output_index, expected, round_up_years):
        # Arrange

        # Create a list of random numbers.
        result_values = [
            112, 125, 9, 72, 170, 146, 157, 148, 20, 170, 24, 27, 39, 156, 123, 76, 67, 56, 38, 50, 48, 49, 147, 55, 66, 133, 141, 41, 39, 41, 43, 135, 142, 74, 119, 118, 75, 11, 163, 15, 81, 162, 32, 167, 144, 53, 97, 99, 3, 17, 76, 27, 15, 2, 160, 151, 7, 150, 4, 69, 117, 37, 52, 32, 34, 50, 3, 153, 135, 167, 107, 71, 35, 13, 140, 24, 157, 34, 115, 6, 23, 149, 126, 67, 78, 41, 112, 75, 0, 144, 15, 8, 109, 50, 152, 137, 91, 145, 12, 162, 26, 42, 91, 120, 102, 75, 97, 133, 37, 41, 41, 11, 159, 109, 86, 102, 83, 56, 61, 104, 124, 66, 12
        ]

        results_for_individual = ApsimResultHelper.create_results_for_individual(
            result_values, [], apsim_output_index
        )

        aggregate_function = TestAggregateFunction([high_low, percentage])

        # Act
        actual = MeanAtHighLowPercentageYears.calculate(aggregate_function, results_for_individual, apsim_output_index, round_up_years)

        # Assert
        message_on_error = f"result_values: {result_values} apsim_output_index: {apsim_output_index} expected: {expected} actual: {actual}"
        self.assertAlmostEqual(first=actual, second=expected, places=2, msg=message_on_error)


    @parameterized.expand([
        ("fred",  "10"),
        ("highest", "-1"),
        ("highest", "101"),
        ("lowest", "-1"),
        ("lowest", "101")
    ])
    def test_calculate_throws(self, high_low, percentage):
        # Arrange

        # Create a list of random numbers.
        result_values = [112, 125, 9, 72, 170, 146, 157]

        results_for_individual = ApsimResultHelper.create_results_for_individual(
            result_values, [], 0
        )

        aggregate_function = TestAggregateFunction([high_low, percentage])

        # Act & Assert
        self.assertRaises(Exception, MeanAtHighLowPercentageYears.calculate, aggregate_function, results_for_individual, 0, False)


if __name__ == "__main__":
    unittest.main()
