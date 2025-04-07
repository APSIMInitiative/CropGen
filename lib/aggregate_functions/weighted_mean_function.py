import logging
import numpy as np

from lib.aggregate_functions.weighted_function_helper import WeightedFunctionHelper

class WeightedMeanFunction:
    @staticmethod
    def calculate(
        crop_gen_job, 
        aggregate_function, 
        results_for_individual, 
        apsim_output_index,
        aggregated_data_state
    ):
        if not results_for_individual:
            logging.error("No results available for calculating weighted mean.")
            return 0.0

        proportional_yields = WeightedFunctionHelper.get_or_compute_proportional_yields(
            crop_gen_job,
            aggregate_function,
            results_for_individual,
            apsim_output_index,
            aggregated_data_state
        )

        if not proportional_yields:
            logging.error("No proportional yields available for calculating weighted mean.")
            return 0.0

        return np.average(proportional_yields)
