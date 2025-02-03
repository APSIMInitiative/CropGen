import json
import datetime

#
# A base class model. Simply provides a to json routine.
#
class Model:
    #
    # Serialises itself to JSON.
    #
    def to_json(self, pretty_print=False):
        indent = 4 if pretty_print else None
        
        json_str = json.dumps(
            self, 
            default=lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else obj.__dict__,
            separators=(',', ':'),
            indent=indent
        )
        
        return json_str
    
    #
    # Converts the passed in json object to lowercase, recursively.
    #
    def convert_to_lower_case_recursive(self, json_object):
        if isinstance(json_object, dict):
            return {k.lower(): self.convert_to_lower_case_recursive(v) for k, v in json_object.items()}
        elif isinstance(json_object, list):
            return [self.convert_to_lower_case_recursive(item) for item in json_object]
        else:
            return json_object
