from json.decoder import JSONDecodeError
import json

from lib.models.common.model import Model
from lib.models.cgm.apsim_result import ApsimResult
from lib.utils.json_helper import JsonHelper

#
# A WGP Server Response, as returned from the WGP Server.
#
class RunApsimResponse(Model):
    #
    # Constructor
    #
    def __init__(self):
        self.JobID = ''
        self.ID = 0
        self.Fields = []
        self.Rows = []
        self.RunTime = 0.0
        self.RunSource = ''

    #
    # Parses the JSON data into this class.
    #
    def parse_from_json_string(self, message):
        errors = []
        try:
            json_object = json.loads(message)
            self.JobID = JsonHelper.get_attribute(json_object, 'JobID', errors)
            self.ID = JsonHelper.get_attribute(json_object, 'ID', errors)
            self.Fields = JsonHelper.get_attribute(json_object, 'Fields', errors)
            self.Rows = self._parse_apsim_results(json_object, errors)
            self.RunTime = JsonHelper.get_attribute(json_object, 'RunTime', errors)
            self.RunSource = JsonHelper.get_attribute(json_object, 'RunSource', errors)
        except JSONDecodeError as error:
            errors.append(f"Failed to parse {self.get_type_name()} JSON: '{message}'. Error: '{error}'")
        return errors

    #
    # Parses the rows into a collection of apsim simulation responses.
    #
    def _parse_apsim_results(self, json_object, errors):
         apsim_results = []

         results = JsonHelper.get_attribute(json_object, 'Rows', errors)

         if results:
            # Iterate over all of the results
            for result in results:
                apsim_result = ApsimResult()
                apsim_result.parse_from_json_object(result, errors)
                apsim_results.append(apsim_result)

         return apsim_results
    
    #
    # Searches for an APSIM result for the given individual, or returns None
    # if no APSIM result can be found for that individual.
    #
    def get_apsim_results_for_individual(self, individual):
        apsim_results = []
        for row in self.Rows:
            if row.ID == individual:
              apsim_results.append(row)
        return apsim_results

    #
    # Returns the type name.
    #
    def get_type_name(self):
        return __class__.__name__