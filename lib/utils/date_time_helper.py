from tzlocal import get_localzone
from datetime import datetime
from datetime import timedelta

#
# Simple date time helper class
#
class DateTimeHelper():
    # Constants
    DATE_FORMAT = '%Y-%m-%d'
    TIME_FORMAT = '%H.%M.%S'
    DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
    DATE_TIME_FORMAT_DIR = "%Y-%m-%d %H-%M-%S"

    #
    # Gets the full date time as a DateTime object.
    #
    @staticmethod
    def get_date_time():
        return datetime.now()
    
    #
    # Creates a date time from a given string
    #
    @staticmethod
    def get_date_from_str(date_time_str, date_format=DATE_FORMAT):
        return datetime.strptime(date_time_str, date_format)
    
    #
    # returns a date time with only the year replaced
    #
    @staticmethod
    def update_date_time_year(date_time, year):
        return date_time.replace(year=year)
    
    #
    # Converts a date to a string in the given format.
    #
    def date_to_str(date, date_format=DATE_FORMAT):
        return date.strftime(date_format)

    #
    # Gets the seconds since now and the start time provided.
    #
    @staticmethod
    def get_elapsed_seconds_since(start_date_time):
        end_date_time = DateTimeHelper.get_date_time()
        delta = end_date_time - start_date_time
        return delta.total_seconds()
    
    #
    # Gets the time since now as a time string.
    #
    @staticmethod
    def get_elapsed_time_since(start_date_time):
        return DateTimeHelper.seconds_to_hhmmss_ms(
            DateTimeHelper.get_elapsed_seconds_since(start_date_time)
        )
    
    #
    # convert seconds to hh:mm:ss
    #
    @staticmethod
    def seconds_to_hhmmss_ms(seconds):
        # Calculate the hours, minutes, and remaining seconds
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        # Extract milliseconds
        milliseconds = int((seconds % 1) * 1000)
        
        # Create a formatted time string
        time_string = '{:02d}:{:02d}:{:02d}.{:03d}'.format(hours, minutes, seconds, milliseconds)
        
        return time_string
    
    #
    # Adds the seconds to the current date time and return a formatted string.
    #
    @staticmethod
    def add_seconds_to_datetime_now(seconds):
        local_timezone = get_localzone()
        now = datetime.now(local_timezone)
        new_datetime = now + timedelta(seconds=seconds)
        # Get the current datetime with timezone
        formatted_datetime = new_datetime.strftime("%Y-%m-%d %H:%M:%S:%f %Z%z")
        return formatted_datetime

    #
    # Gets now as a date (no time) string.
    #
    @staticmethod
    def get_date_now_str():
        return DateTimeHelper._get_now_str(DateTimeHelper.DATE_FORMAT)

    #
    # Gets now as a time (no date) string.
    #
    @staticmethod
    def get_time_now_str():
        return DateTimeHelper._get_now_str(DateTimeHelper.TIME_FORMAT)

    #
    # Gets now as a datetime string.
    #
    @staticmethod
    def get_date_time_now_str():
        return DateTimeHelper._get_now_str(DateTimeHelper.DATE_TIME_FORMAT)
    

    #
    # Gets now as a datetime string.
    #
    @staticmethod
    def get_date_time_now_str_dir_format():
        return DateTimeHelper._get_now_str(DateTimeHelper.DATE_TIME_FORMAT_DIR)

    #
    # Helper that others call into, passing only the format.
    #
    @staticmethod
    def _get_now_str(format):
        return datetime.now().strftime(format)
