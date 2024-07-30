import logging

from lib.server.cropgen_runner import CropGenRunner
from lib.logging.logger_config import LoggerConfig
from lib.config.config import Config
from lib.utils.environment_variables_provider import EnvironmentVariablesProvider

# Main entry point
if __name__ == "__main__":
    try:
        env_provider = EnvironmentVariablesProvider()
        config = Config(env_provider)
        config._parse()
        logger_config = LoggerConfig(config, env_provider)
        logger_config.setup_logger(True)        
        crop_gen_runner = CropGenRunner(config, env_provider)

        logging.info("Starting main job polling routine. Polling for jobs every %d seconds", config.SleepBetweenJobsSeconds)

        while True:
            try:
                crop_gen_runner.poll_for_job_and_run()
            except KeyboardInterrupt:
                logging.info("Keyboard interrupt. Exiting...")
                break

        logging.info("Closing CropGen application")
    except:
        logging.exception("Exception - CropGen Main Application catch handler")
