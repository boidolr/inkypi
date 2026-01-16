#!/usr/bin/env python3
"""
Shutdown script for InkyPi display.
Clears the display and puts it into powersave/sleep mode before service stops.
"""

import logging
import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from config import Config  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def shutdown_display():
    """Clear the display and set it to powersave mode."""
    exit_code = 1
    try:
        logger.info("Starting display shutdown sequence")

        # Load device config
        device_config = Config()
        display_type = device_config.get_config("display_type", default="inky")

        logger.info("Display type: %s", display_type)

        # Handle different display types
        if display_type == "mock":
            logger.info("Mock display detected, no hardware shutdown needed")
            exit_code = 0
        elif display_type == "inky":
            try:
                from PIL import Image  # noqa: PLC0415

                from display.inky_display import InkyDisplay  # noqa: PLC0415
                display = InkyDisplay(device_config)

                # Clear the display by showing a white image
                width, height = device_config.get_resolution()
                white_image = Image.new("RGB", (width, height), (255, 255, 255))

                logger.info("Clearing Inky display")
                display.inky_display.set_image(white_image)
                display.inky_display.show()
                logger.info("Inky display cleared successfully")
                exit_code = 0

            except Exception:
                logger.exception("Error clearing Inky display")

        else:
            # Waveshare or other EPD display
            try:
                from display.waveshare_display import WaveshareDisplay  # noqa: PLC0415
                display = WaveshareDisplay(device_config)

                logger.info("Clearing Waveshare display")
                # Initialize display to wake it up
                display.epd_display_init()
                # Clear the display
                display.epd_display.Clear()
                logger.info("Waveshare display cleared")

                # Put display into sleep mode for power saving
                logger.info("Putting Waveshare display into sleep mode")
                display.epd_display.sleep()
                logger.info("Waveshare display in sleep mode")
                exit_code = 0

            except Exception:
                logger.exception("Error shutting down Waveshare display")

        if exit_code == 0:
            logger.info("Display shutdown sequence completed successfully")
        else:
            logger.info("Display shutdown encountered errors")
        return exit_code  # noqa: TRY300

    except Exception:
        logger.exception("Unexpected error during display shutdown")
        return 1


if __name__ == "__main__":
    exit_code = shutdown_display()
    sys.exit(exit_code)
