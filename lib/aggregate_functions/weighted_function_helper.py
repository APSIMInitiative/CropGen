import logging

class WeightedFunctionHelper:

    SOWING_DATE_PARAM = 0
    SITE_PARAM = 1    

    @staticmethod
    def get_sowing_date_output_name(aggregate_function):
        return aggregate_function.get_param_by_index(WeightedFunctionHelper.SOWING_DATE_PARAM)
    
    
    @staticmethod
    def get_site_output_name(aggregate_function):
        return aggregate_function.get_param_by_index(WeightedFunctionHelper.SITE_PARAM)
    
    
    @staticmethod
    def get_text_output_index(name, text_outputs):
        name = name.strip().lower()
        for index, text_output in enumerate(text_outputs):
            if text_output.apsimOutputName.strip().lower() == name:
                return index
        return None


    @staticmethod
    def validate_weighted_mean_params(sowing_date_output_name, site_output_name, sowing_date_weighting):
        missing_params = []
        if not sowing_date_output_name:
            missing_params.append(f"Sowing date text output name (Param index {WeightedFunctionHelper.SOWING_DATE_PARAM})")
        if not site_output_name:
            missing_params.append(f"Site text output name (Param index {WeightedFunctionHelper.SITE_PARAM})")
        if not sowing_date_weighting:
            missing_params.append("Job Config Sowing Date Weighting")

        if missing_params:
            raise ValueError("Weighted Mean Function is missing required parameters: %s", ", ".join(missing_params))
    

    @staticmethod
    def validate_text_output_indexes(sowing_date_output_name, sowing_date_index, site_output_name, site_name_index):
        missing_params = []

        # Check for invalid sowing date index and include the sowing date output name in the error message
        if sowing_date_index is None or sowing_date_index < 0:
            missing_params.append(f"Sowing date index for '{sowing_date_output_name}' (Param index {WeightedFunctionHelper.SOWING_DATE_PARAM})")

        # Check for invalid site name index and include the site output name in the error message
        if site_name_index is None or site_name_index < 0:
            missing_params.append(f"Site name index for '{site_output_name}' (Param index {WeightedFunctionHelper.SITE_PARAM})")

        # If there are missing parameters, log the error and return False
        if missing_params:
            raise ValueError("Weighted Mean Function is missing required parameters: %s", ", ".join(missing_params))
        
        
    @staticmethod
    def extract_site_and_sowing_date(text_outputs, result, site_name_index, sowing_date_index):
        site_output = text_outputs[site_name_index]
        site_name = site_output.extract_match(result.text_values[site_name_index]).strip().lower()
        
        sowing_date_output = text_outputs[sowing_date_index]
        sowing_date = sowing_date_output.extract_match(result.text_values[sowing_date_index]).strip().lower()

        return site_name, sowing_date
