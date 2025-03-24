import logging
import random
import numpy as np
from collections import defaultdict

from lib.aggregate_functions.weighted_function_helper import WeightedFunctionHelper

class WeightedMeanFunction:

    @staticmethod
    def calculate(crop_gen_job, aggregate_function, results_for_individual, apsim_output_index):

        if not results_for_individual:
            return 0.0
        
        sowing_date_output_name, site_output_name, sowing_date_weighting = WeightedMeanFunction.extract_weighting_data(crop_gen_job, aggregate_function)
        sowing_date_index, site_name_index = WeightedMeanFunction.validate_and_get_indexes(crop_gen_job, sowing_date_output_name, site_output_name)
        proportional_yields = WeightedMeanFunction.compute_proportional_yields(crop_gen_job.text_outputs, results_for_individual, sowing_date_weighting, sowing_date_index, site_name_index, apsim_output_index)
        
        return np.average(proportional_yields) if proportional_yields else 0


    @staticmethod
    def extract_weighting_data(crop_gen_job, aggregate_function):
        sowing_date_output_name = WeightedFunctionHelper.get_sowing_date_output_name(aggregate_function)
        site_output_name = WeightedFunctionHelper.get_site_output_name(aggregate_function)
        sowing_date_weighting = crop_gen_job.sowingDateWeighting

        WeightedFunctionHelper.validate_weighted_mean_params(
            sowing_date_output_name, site_output_name, sowing_date_weighting
        )

        return sowing_date_output_name, site_output_name, sowing_date_weighting


    @staticmethod
    def validate_and_get_indexes(crop_gen_job, sowing_date_output_name, site_output_name):
        sowing_date_index = WeightedFunctionHelper.get_text_output_index(
            sowing_date_output_name, crop_gen_job.text_outputs
        )
        site_name_index = WeightedFunctionHelper.get_text_output_index(
            site_output_name, crop_gen_job.text_outputs
        )

        WeightedFunctionHelper.validate_text_output_indexes(
            sowing_date_output_name, sowing_date_index, site_output_name, site_name_index
        )

        return sowing_date_index, site_name_index


    @staticmethod
    def compute_proportional_yields(
        text_outputs, 
        results_for_individual, 
        sowing_date_weighting, 
        sowing_date_index, 
        site_name_index, 
        apsim_output_index
    ):        
        proportional_yields = []
        
        # The first step is to categorize the results by site and sowing date
        categorized_results = WeightedMeanFunction.categorize_results(
            results_for_individual, text_outputs, site_name_index, sowing_date_index
        )

        # Now that the results are categorized, we can compute the proportional yields
        proportional_yields = WeightedMeanFunction.compute_proportional_yields_from_categories(
            categorized_results, sowing_date_weighting, apsim_output_index
        )

        # Log the final output
        if proportional_yields:
            mean_yield = sum(proportional_yields) / len(proportional_yields)
            logging.info(f"Proportional Yield Mean: {mean_yield}")
        else:
            logging.warning("No proportional yields available.")

        return proportional_yields
    

    @staticmethod
    def categorize_results(results_for_individual, text_outputs, site_name_index, sowing_date_index):
        categorized_results = defaultdict(list)

        for apsim_result in results_for_individual:
            site_name, sowing_date = WeightedFunctionHelper.extract_site_and_sowing_date(
                text_outputs, apsim_result, site_name_index, sowing_date_index
            )

            if site_name and sowing_date:
                categorized_results[(site_name, sowing_date)].append(apsim_result)

        return categorized_results


    @staticmethod
    def compute_proportional_yields_from_categories(categorized_results, sowing_date_weighting, apsim_output_index):
        proportional_yields = []

        for (site_name, sowing_date), results in categorized_results.items():
            site_data = sowing_date_weighting.get(site_name)
            if site_data:
                weight = site_data.weights.get(sowing_date)
            
                if weight is not None:
                    result_values = [res.values[apsim_output_index] for res in results]
                    num_samples = round(len(result_values) * weight)
                    proportional_sowing_yields = random.choices(result_values, k=num_samples)
                    proportional_yields.extend(proportional_sowing_yields)
            else:
                logging.warning(f"No sowing date weighting data for site: {site_name}")

        return proportional_yields
