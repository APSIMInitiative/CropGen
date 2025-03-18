from lib.models.common.model import Model
from lib.utils.json_helper import JsonHelper

class Weight(Model):
    def __init__(self, sowing_date, weight):
        self.sowing_date = sowing_date
        self.weight = weight

class SowingDateWeighting(Model):
    def __init__(self, site_name, weights):
        self.site_name = site_name
        self.weights = weights

    @staticmethod
    def parse_from_json_object(json_object, errors):
        weighting_list = JsonHelper.get_non_mandatory_attribute(json_object, 'sowingDateWeighting', True, [])
        if weighting_list is None:
            return []

        parsed_weighting = []
        for weighting_entry in weighting_list:
            site_name = JsonHelper.get_attribute(weighting_entry, 'siteName', errors, True)
            weights_json = JsonHelper.get_non_mandatory_attribute(weighting_entry, 'weights', True, [])
            
            weights = []
            for weight_entry in weights_json:
                sowing_date = JsonHelper.get_attribute(weight_entry, 'sowingDate', errors, True)
                weight = JsonHelper.get_non_mandatory_attribute(weight_entry, 'weight', True, None)
                
                weights.append(Weight(sowing_date, weight))

            parsed_weighting.append(SowingDateWeighting(site_name, weights))
        
        return parsed_weighting
    
    @staticmethod
    def get_type_name():
        return __class__.__name__
