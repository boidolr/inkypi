import logging
import random
from pathlib import Path

from PIL import Image
from PIL import ImageColor
from PIL import ImageOps

from plugins.base_plugin.base_plugin import BasePlugin
from utils.image_utils import pad_image_blur

logger = logging.getLogger(__name__)


class ImageUpload(BasePlugin):
    def open_image(self, img_index: int, image_locations: list) -> Image.Image:
        if not image_locations:
            msg = "No images provided."
            raise RuntimeError(msg)
        # Open the image using Pillow
        try:
            image = Image.open(image_locations[img_index])
        except Exception:
            msg = "Failed to read image file."
            logger.exception(msg)
            raise RuntimeError(msg)
        return image

    def generate_image(self, settings, device_config) -> Image.Image:
        # Get the current index from the device json
        img_index = settings.get("image_index", 0)
        image_locations = settings.get("imageFiles[]")

        if img_index >= len(image_locations):
            # Prevent Index out of range issues when file list has changed
            img_index = 0

        if settings.get("randomize") == "true":
            img_index = random.randrange(0, len(image_locations))
            image = self.open_image(img_index, image_locations)
        else:
            image = self.open_image(img_index, image_locations)
            img_index = (img_index + 1) % len(image_locations)

        # Write the new index back ot the device json
        settings["image_index"] = img_index
        orientation = device_config.get_config("orientation")

        if settings.get("padImage") == "true":
            dimensions = device_config.get_resolution()
            if orientation == "vertical":
                dimensions = dimensions[::-1]

            if settings.get("backgroundOption") == "blur":
                return pad_image_blur(image, dimensions)
            background_color = ImageColor.getcolor(settings.get("backgroundColor") or (255, 255, 255), "RGB")
            return ImageOps.pad(
                image,
                dimensions,
                color=background_color,
                method=Image.Resampling.LANCZOS,
            )
        return image

    def cleanup(self, settings) -> None:
        """Delete all uploaded image files associated with this plugin instance."""
        image_locations = settings.get("imageFiles[]", [])
        if not image_locations:
            return

        for image_path in image_locations:
            image_file = Path(image_path)
            if image_file.exists():
                try:
                    image_file.unlink()
                    logger.info(f"Deleted uploaded image: {image_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete uploaded image {image_path}: {e}")
