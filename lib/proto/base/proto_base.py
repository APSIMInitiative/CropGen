import json

class ProtoBase:
    def to_json(self, pretty_print=False):
        indent = None
        if pretty_print: indent = 4        
        json_str = json.dumps(
            self, 
            default = lambda
            obj: obj.__dict__,
            separators=(',', ':'),
            indent=indent
        )

        return json_str
    
    def get_type_name(self):
        pass
