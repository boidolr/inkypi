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

from config import Config
from display.display_manager import DisplayManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def shutdown_display():
    """Clear the display and set it to powersave mode."""
    try:
        logger.info("Starting display shutdown sequence")
        
        # Load device config
        device_config = Config()
        display_type = device_config.get_config("display_type", default="inky")
        
        logger.info(f"Display type: {display_type}")
        
        # Handle different display types
        if display_type == "mock":
            logger.info("Mock display detected, no hardware shutdown needed")
            return 0
            
        elif display_type == "inky":
            try:
                from display.inky_display import InkyDisplay
                display = InkyDisplay(device_config)
                
                # Clear the display by showing a white image
                from PIL import Image
                width, height = device_config.get_resolution()
                white_image = Image.new("RGB", (width, height), (255, 255, 255))
                
                logger.info("Clearing Inky display")
                display.inky_display.set_image(white_image)
                display.inky_display.show()
                logger.info("Inky display cleared successfully")
                
            except Exception as e:
                logger.error(f"Error clearing Inky display: {e}")
                return 1
                
        else:
            # Waveshare or other EPD display
            try:
                from display.waveshare_display import WaveshareDisplay
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
                
            except Exception as e:
                logger.error(f"Error shutting down Waveshare display: {e}")
                return 1
        
        logger.info("Display shutdown sequence completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error during display shutdown: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = shutdown_display()
    sys.exit(exit_code)
