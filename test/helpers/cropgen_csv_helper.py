import csv
import os
from lib.proto.messages.apsim_result import ApsimResult

class CropGenCsvHelper:
    def __init__(self, csv_filename):
        self.csv_path = os.path.join("test", "files", csv_filename)

    def parse(self):
        try:
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                apsim_results = []

                for row in reader:
                    sowing_date = row["SowingDate"].strip()
                    yield_value = float(row["Yield"])
                    evapotranspiration = float(row["Evapotranspiration"])
                    site = row["Site"].strip()

                    apsim_results.append(
                        self.generate_apsim_result(
                            [yield_value, evapotranspiration],
                            [sowing_date, site]
                        )
                    )

                return apsim_results

        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        except KeyError as e:
            raise ValueError(f"Missing expected column in CSV: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid data format in CSV: {e}")
        

    def generate_apsim_result(self, output_values, text_values):
        apsim_result = ApsimResult()
        apsim_result.values = output_values
        apsim_result.text_values = text_values
        return apsim_result