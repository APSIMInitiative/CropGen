import logging
import numpy as np
from collections import defaultdict

class WeightedFunctionHelper:

    # Constants to define parameter indices for sowing date and site
    SOWING_DATE_PARAM = 0
    SITE_PARAM = 1    

    @staticmethod
    def get_sowing_date_output_name(aggregate_function):
        """Retrieves the sowing date output name from the aggregate function parameters."""
        return aggregate_function.get_param_by_index(WeightedFunctionHelper.SOWING_DATE_PARAM)
    

    @staticmethod
    def get_site_output_name(aggregate_function):
        """Retrieves the site output name from the aggregate function parameters."""
        return aggregate_function.get_param_by_index(WeightedFunctionHelper.SITE_PARAM)
    

    @staticmethod
    def get_text_output_index(name, text_outputs):
        """
        Finds the index of a text output by matching its name (case-insensitive).
        
        :param name: The name to search for.
        :param text_outputs: List of text output objects.
        :return: The index of the matching output or None if not found.
        """
        name = name.strip().lower()
        for index, text_output in enumerate(text_outputs):
            if text_output.apsimOutputName.strip().lower() == name:
                return index
        return None


    @staticmethod
    def validate_weighted_mean_params(sowing_date_output_name, site_output_name, sowing_date_weighting):
        """
        Validates required parameters for computing the weighted mean.
        
        Raises a ValueError if any required parameter is missing.
        """
        missing_params = []
        if not sowing_date_output_name:
            missing_params.append(f"Sowing date text output name (Param index {WeightedFunctionHelper.SOWING_DATE_PARAM})")
        if not site_output_name:
            missing_params.append(f"Site text output name (Param index {WeightedFunctionHelper.SITE_PARAM})")
        if not sowing_date_weighting:
            missing_params.append("Job Config Sowing Date Weighting")

        if missing_params:
            raise ValueError("Weighted Mean Function is missing required parameters: %s" % ", ".join(missing_params))
    

    @staticmethod
    def validate_text_output_indexes(sowing_date_output_name, sowing_date_index, site_output_name, site_name_index):
        """
        Validates that the extracted text output indexes are valid (not None or negative).
        
        Raises a ValueError if any required index is missing or invalid.
        """
        missing_params = []

        if sowing_date_index is None or sowing_date_index < 0:
            missing_params.append(f"Sowing date index for '{sowing_date_output_name}' (Param index {WeightedFunctionHelper.SOWING_DATE_PARAM})")

        if site_name_index is None or site_name_index < 0:
            missing_params.append(f"Site name index for '{site_output_name}' (Param index {WeightedFunctionHelper.SITE_PARAM})")

        if missing_params:
            raise ValueError("Weighted Mean Function is missing required parameters: %s" % ", ".join(missing_params))
        
        
    @staticmethod
    def extract_site_and_sowing_date(text_outputs, result, site_name_index, sowing_date_index):
        """
        Extracts site name and sowing date values from text output based on given indexes.
        
        :param text_outputs: List of text output objects.
        :param result: The result object containing text values.
        :param site_name_index: The index of the site name in text outputs.
        :param sowing_date_index: The index of the sowing date in text outputs.
        :return: Tuple (site_name, sowing_date) with both values converted to lowercase.
        """
        site_output = text_outputs[site_name_index]
        site_name = site_output.extract_match(result.text_values[site_name_index]).strip().lower()
        
        sowing_date_output = text_outputs[sowing_date_index]
        sowing_date = sowing_date_output.extract_match(result.text_values[sowing_date_index]).strip().lower()

        return site_name, sowing_date
    

    @staticmethod
    def extract_weighting_data(crop_gen_job, aggregate_function):
        """
        Extracts and validates sowing date weighting data from the crop generation job.
        
        :param crop_gen_job: The job object containing weighting configurations.
        :param aggregate_function: The function that determines sowing date and site parameters.
        :return: Tuple (sowing_date_output_name, site_output_name, sowing_date_weighting).
        """
        sowing_date_output_name = WeightedFunctionHelper.get_sowing_date_output_name(aggregate_function)
        site_output_name = WeightedFunctionHelper.get_site_output_name(aggregate_function)
        sowing_date_weighting = crop_gen_job.sowingDateWeighting

        # Ensure all necessary parameters are present
        WeightedFunctionHelper.validate_weighted_mean_params(
            sowing_date_output_name, site_output_name, sowing_date_weighting
        )

        return sowing_date_output_name, site_output_name, sowing_date_weighting
    

    @staticmethod
    def validate_and_get_indexes(crop_gen_job, sowing_date_output_name, site_output_name):
        """
        Retrieves and validates the text output indexes for sowing date and site name.
        
        :param crop_gen_job: The job object containing text outputs.
        :param sowing_date_output_name: The expected name of the sowing date output.
        :param site_output_name: The expected name of the site output.
        :return: Tuple (sowing_date_index, site_name_index).
        """
        sowing_date_index = WeightedFunctionHelper.get_text_output_index(
            sowing_date_output_name, crop_gen_job.text_outputs
        )
        site_name_index = WeightedFunctionHelper.get_text_output_index(
            site_output_name, crop_gen_job.text_outputs
        )

        # Validate indexes
        WeightedFunctionHelper.validate_text_output_indexes(
            sowing_date_output_name, sowing_date_index, site_output_name, site_name_index
        )

        return sowing_date_index, site_name_index
    

    @staticmethod
    def categorize_results(results_for_individual, text_outputs, site_name_index, sowing_date_index, apsim_output_index):
        """
        Categorizes APSIM results based on site name and sowing date.
        
        :param results_for_individual: List of APSIM result objects.
        :param text_outputs: List of text output objects.
        :param site_name_index: The index of site name in text outputs.
        :param sowing_date_index: The index of sowing date in text outputs.
        :param apsim_output_index: The index of APSIM output values.
        :return: Dictionary with keys as (site_name, sowing_date) and values as lists of output values.
        """
        categorized_results = defaultdict(list)

        for apsim_result in results_for_individual:
            site_name, sowing_date = WeightedFunctionHelper.extract_site_and_sowing_date(
                text_outputs, apsim_result, site_name_index, sowing_date_index
            )

            if site_name and sowing_date:
                output_result = apsim_result.values[apsim_output_index]
                categorized_results[(site_name, sowing_date)].append(output_result)

        return categorized_results
    
    
    @staticmethod
    def compute_proportional_values_from_categories(categorized_results, sowing_date_weighting):
        """
        Computes proportional values based on the weighted sowing dates.
        Applies weighting to sampled APSIM output values according to the provided sowing date weighting.
        
        :param categorized_results: Dictionary of categorized APSIM output values.
        :param sowing_date_weighting: Dictionary containing weighting information per site.
        :return: A list of proportional values sampled based on weighting.
        """
        proportional_values = []

        # Track sites without weighting data
        missing_sites = set()

        for (site_name, sowing_date), result_values in categorized_results.items():
            site_data = sowing_date_weighting.get(site_name)

            if not site_data:
                missing_sites.add(site_name)
                continue

            weight = site_data.weights.get(sowing_date)
            if weight is None:
                continue

            num_samples = round(len(result_values) * weight)
            if num_samples == 0:
                continue

            # Sample values proportionally and add them to the results
            proportional_values.extend(
                np.random.choice(
                    result_values, 
                    num_samples, 
                    replace=True
                ).tolist()
            )

        # Log missing sites at the end to avoid redundant warnings
        if missing_sites:
            logging.warning(f"No sowing date weighting data for sites: {', '.join(missing_sites)}")

        return proportional_values


    @staticmethod
    def compute_proportional(
        text_outputs, 
        results_for_individual, 
        sowing_date_weighting, 
        sowing_date_index, 
        site_name_index, 
        apsim_output_index
    ):        
        """
        Computes proportional values based on categorized APSIM results using sowing date weighting.

        This method categorizes the APSIM results by site and sowing date, then computes 
        the proportional values based on the provided sowing date weighting. The proportional 
        values are calculated by applying a weight for each sowing date for a given site, 
        and then randomly sampling the corresponding result values according to the weight.

        Parameters:
        - text_outputs: List of text outputs that contain site and sowing date information.
        - results_for_individual: List of APSIM result objects that need to be categorized.
        - sowing_date_weighting: Weighting information for sowing dates per site.
        - sowing_date_index: Index to extract the sowing date information from the results.
        - site_name_index: Index to extract the site name information from the results.
        - apsim_output_index: Index to extract the APSIM output values from the results.

        Returns:
        - List of proportional values computed based on the categorized results and sowing date weighting.
        """
        
        # Initialize an empty list to store proportional values
        proportional_values = []

        # The first step is to categorize the results by site and sowing date
        categorized_results = WeightedFunctionHelper.categorize_results(
            results_for_individual, text_outputs, site_name_index, sowing_date_index, apsim_output_index
        )

        # Now that the results are categorized, we can compute the proportional values based on the weighting data
        proportional_values = WeightedFunctionHelper.compute_proportional_values_from_categories(
            categorized_results, sowing_date_weighting
        )

        # Return the computed proportional values
        return proportional_values
