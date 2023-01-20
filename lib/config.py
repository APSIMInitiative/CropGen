import json
import os

class Config:
  def __init__(self):

    relative_path = '../config/config.json'
    current_script_dir = os.path.dirname(os.path.realpath(__file__))
    config_file_full_path = os.path.join(current_script_dir, relative_path)

    with open(config_file_full_path) as json_config_file:
        data = json.load(json_config_file)    
    
    self.jobs_base_url = data['jobsBaseUrl']
    self.sim_gen_url = data['simGenUrl']