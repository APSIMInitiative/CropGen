from lib.utils.date_time_helper import DateTimeHelper

#
# Simple wrapper for generating dates for a given season.
#
class APSIMSeasonDateGenerator():
    
    #
    # Constructor
    #
    def __init__(self, config, apsim_clock_start_date):
        self.apsim_clock_start_date = self.set_start_date(config, apsim_clock_start_date)
        self.config = config

    #
    # Sets the start date. Defaults to the config value but if the param is set it will use this instead.
    #
    def set_start_date(self, config, apsim_clock_start_date):
        start_date_to_use = config.ApsimSimulationStartDate
        if apsim_clock_start_date:
            start_date_to_use = apsim_clock_start_date

        if not start_date_to_use: 
            raise Exception("Cannot use %s because no APSIM clock start date is available", self.get_type_name())
        
        return start_date_to_use

    #
    # Generates a start date for the given season.
    #   
    def generate_start_date_from_season(self, season):
        return self.generate_date_for_season(season, self.config.ApsimSimulationStartDateAddYear, self.config.ApsimClockDateFormat)

    #
    # Generates an end date for the given season.
    #   
    def generate_end_date_from_season(self, season):
        return self.generate_date_for_season(season, self.config.ApsimSimulationEndDateAddYear, self.config.ApsimClockDateFormat)
    
    #
    # Generates the date for a given season.
    #
    def generate_date_for_season(self, season, add_years_to_season, date_format):
        date_time = DateTimeHelper.get_date_from_str(self.apsim_clock_start_date)
        season_date_time = DateTimeHelper.update_date_time_year(date_time, season + add_years_to_season)
        return DateTimeHelper.date_to_str(season_date_time, date_format)

    #
    # Returns the type name.
    #
    @staticmethod
    def get_type_name():
        return __class__.__name__
