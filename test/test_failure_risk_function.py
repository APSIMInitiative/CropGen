import unittest

from parameterized import parameterized
from test.test_base import TestBase
from test.helpers.test_aggregate_function import TestAggregateFunction
from test.helpers.apsim_result_helper import ApsimResultHelper
from lib.aggregate_functions.failure_risk_function import FailureRiskFunction

class FailureRiskFunctionTests(TestBase):

    @parameterized.expand([
        ("<",  "10",    0, 0.75),
        ("<",  "1",     0, 0),
        ("<",  "8",     0, 0.5),
        ("<",  "0",     1, 0),

        ("<=", "10",    0, 1),
        ("<=", "8",     0, 0.75),
        ("<=", "8",     2, 1),

        (">",  "5",     0, 0.5),
        (">",  "1",     0, 0.75),
        (">",  "1",     3, 0),

        (">=", "8",     0, 0.5),
        (">=", "3",     0, 0.5),
        (">=", "3",     3, 0),

        ("==", "2",     0, 0.25),
        ("==", "100",   0, 0),
        ("==", "-90",   0, 0),
        ("==", "2",     2, 0),

        ("!=", "8",     0, 0.75),
        ("!=", "100",   0, 1),
        ("!=", "0",     1, 0)
    ])
    def test_calculate(self, operator, param, apsim_output_index, expected):
        # Arrange
        aggregate_function = TestAggregateFunction([operator, param])
        results_for_individual = ApsimResultHelper.create_results_for_individual(
            [1, 2, 8, 10], [], 0
        )

        # Act
        actual = FailureRiskFunction.calculate(aggregate_function, results_for_individual, apsim_output_index)

        # Assert
        self.assertEqual(actual, expected, f"operator: {operator} param: {param} apsim_output_index: {apsim_output_index} expected: {expected} actual: {actual}")

    @parameterized.expand([
        (None,  "10"),
        ("<<", "-1"),
        (">>", "101"),
        ("<", None)
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
        self.assertRaises(Exception, FailureRiskFunction.calculate, aggregate_function, results_for_individual, 0)


if __name__ == "__main__":
    unittest.main()
