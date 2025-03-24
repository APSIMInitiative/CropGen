from lib.models.common.model import Model
from lib.utils.json_helper import JsonHelper

class Weight(Model):
    def __init__(self, sowing_date, weight):
        self.sowing_date = sowing_date.lower()
        self.weight = weight

class SowingDateWeighting(Model):
    def __init__(self, site_name, weights):
        self.site_name = site_name.lower()
        self.weights = {weight.sowing_date: weight.weight for weight in weights}

    @staticmethod
    def parse_from_json_object(json_object, errors):
        weighting_list = JsonHelper.get_non_mandatory_attribute(json_object, 'SowingDateWeighting', True, [])
        if weighting_list is None:
            return {}

        parsed_weighting = {}

        for weighting_entry in weighting_list:
            site_name = JsonHelper.get_attribute(weighting_entry, 'SiteName', errors, True).lower()
            weights_json = JsonHelper.get_non_mandatory_attribute(weighting_entry, 'Weights', True, [])

            weights = [Weight(JsonHelper.get_attribute(w, 'SowingDate', errors, True), 
                              JsonHelper.get_non_mandatory_attribute(w, 'Weight', True, None)) 
                       for w in weights_json]

            parsed_weighting[site_name] = SowingDateWeighting(site_name, weights)

        return parsed_weighting
    
    @staticmethod
    def get_type_name():
        return __class__.__name__
