import logging
import numpy as np

from lib.aggregate_functions.weighted_function_helper import WeightedFunctionHelper

class WeightedMeanFunction:

    @staticmethod
    def calculate(crop_gen_job, aggregate_function, results_for_individual, apsim_output_index):

        if not results_for_individual:
            logging.error("No results available for calculating weighted mean.")
            return 0.0
        
        sowing_date_output_name, site_output_name, sowing_date_weighting = WeightedFunctionHelper.extract_weighting_data(crop_gen_job, aggregate_function)
        sowing_date_index, site_name_index = WeightedFunctionHelper.validate_and_get_indexes(crop_gen_job, sowing_date_output_name, site_output_name)
        proportional_yields = WeightedFunctionHelper.compute_proportional(crop_gen_job.text_outputs, results_for_individual, sowing_date_weighting, sowing_date_index, site_name_index, apsim_output_index)
        
        if not proportional_yields:
            logging.error("No proportional yields available for calculating weighted mean.")
            return 0.0

        return np.average(proportional_yields)