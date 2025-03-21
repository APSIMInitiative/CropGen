import json
import os

from lib.models.run.crop_gen_job import CropGenJob

class CropGenJobHelper:
    def __init__(self, json_filename):
        self.json_path = os.path.join("test", "files", json_filename)

    def parse(self):
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            
            crop_gen_job = CropGenJob()
            crop_gen_job.parse_from_json_object(json_data)
            return crop_gen_job

        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {self.json_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in file: {self.json_path}")
