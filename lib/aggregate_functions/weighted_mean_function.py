import logging

from lib.aggregate_functions.weighted_function_helper import WeightedFunctionHelper

class WeightedMeanFunction:

    SOWING_DATE_PARAM = 0
    SITE_PARAM = 1

    @staticmethod
    def calculate(crop_gen_job, aggregate_function, results_for_individual, apsim_output_index):

        sowing_date_output_name = WeightedFunctionHelper.get_sowing_date_output_name(aggregate_function)
        site_output_name = WeightedFunctionHelper.get_site_output_name(aggregate_function)
        sowing_date_weighting = crop_gen_job.sowingDateWeighting

        if not WeightedFunctionHelper.validate_weighted_mean_params(sowing_date_output_name, site_output_name, sowing_date_weighting):
            raise ValueError(f"Failed validation for weighted mean parameters: Sowing Date Output Name: {sowing_date_output_name}, Site Output Name: {site_output_name}, Weighting: {sowing_date_weighting}")
        
        sowing_date_index = WeightedFunctionHelper.get_text_output_index(sowing_date_output_name, crop_gen_job.text_outputs)
        site_name_index = WeightedFunctionHelper.get_text_output_index(site_output_name, crop_gen_job.text_outputs)

        if not WeightedFunctionHelper.validate_text_output_indexes(sowing_date_output_name, sowing_date_index, site_output_name, site_name_index):
            raise ValueError(f"Failed validation for text output indexes: Sowing Date Index: {sowing_date_index}, Site Name Index: {site_name_index}")
        
        return 0
