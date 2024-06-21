import logging

from lib.server.cropgen_runner import CropGenRunner

# Main entry point
if __name__ == "__main__":
    try:
        crop_gen_runner = CropGenRunner()

        # Run the loop forever until a keyboard event occurs
        while True:
            try:
                crop_gen_runner.run()
            except KeyboardInterrupt: 
                # Break out of the loop on a keyboard event
                logging.info("Keyboard interrupt. Exiting...")
                break

        logging.info("Closing CropGen application")
    except:
        logging.exception("Exception - CropGen Main Application catch handler")
