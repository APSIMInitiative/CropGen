import logging.config
import os.path

# Simple script setup the logger using the config ini file.
logger_config = "logger_config.ini"
logging_config_path = os.path.join(os.path.dirname(__file__), logger_config)
logging.config.fileConfig(logging_config_path)