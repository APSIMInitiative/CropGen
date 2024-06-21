import logging

from lib.server.cropgen_runner import CropGenRunner
from lib.logging.logger_config import LoggerConfig
from lib.config.crop_gen_config import CropGenConfig

# Main entry point
if __name__ == "__main__":
    try:
        config = CropGenConfig()
        config._parse()
        logger_config = LoggerConfig(config)
        logger_config.setup_logger(True)
        crop_gen_runner = CropGenRunner(config)

        while True:
            try:
                crop_gen_runner.poll_for_job_and_run()
            except KeyboardInterrupt:
                logging.info("Keyboard interrupt. Exiting...")
                break

        logging.info("Closing CropGen application")
    except:
        logging.exception("Exception - CropGen Main Application catch handler")
