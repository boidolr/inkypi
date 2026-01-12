import hashlib
import logging
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter
from PIL import ImageOps

logger = logging.getLogger(__name__)


def get_image(image_url: str) -> Image.Image | None:
    response = requests.get(image_url)
    if 200 <= response.status_code < 300 or response.status_code == 304:
        return Image.open(BytesIO(response.content))
    else:
        logger.error(f"Received non-200 response from {image_url}: status_code: {response.status_code}")
        return None


def change_orientation(image, orientation, inverted=False):
    if orientation == "horizontal":
        angle = 0
    elif orientation == "vertical":
        angle = 90

    if inverted:
        angle = (angle + 180) % 360

    return image.rotate(angle, expand=1)


def resize_image(image, desired_size, image_settings=None):
    if image_settings is None:
        image_settings = []
    img_width, img_height = image.size
    desired_width, desired_height = desired_size
    desired_width, desired_height = int(desired_width), int(desired_height)

    img_ratio = img_width / img_height
    desired_ratio = desired_width / desired_height

    keep_width = "keep-width" in image_settings

    x_offset, y_offset = 0, 0
    new_width, new_height = img_width, img_height
    # Step 1: Determine crop dimensions
    desired_ratio = desired_width / desired_height
    if img_ratio > desired_ratio:
        # Image is wider than desired aspect ratio
        new_width = int(img_height * desired_ratio)
        if not keep_width:
            x_offset = (img_width - new_width) // 2
    else:
        # Image is taller than desired aspect ratio
        new_height = int(img_width / desired_ratio)
        if not keep_width:
            y_offset = (img_height - new_height) // 2

    # Step 2: Crop the image
    image = image.crop((x_offset, y_offset, x_offset + new_width, y_offset + new_height))

    # Step 3: Resize to the exact desired dimensions (if necessary)
    return image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)


def apply_image_enhancement(img, image_settings=None):
    # Convert image to RGB mode if necessary for enhancement operations
    # ImageEnhance requires RGB mode for operations like blend
    if image_settings is None:
        image_settings = {}
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    # Apply Brightness
    img = ImageEnhance.Brightness(img).enhance(image_settings.get("brightness", 1.0))

    # Apply Contrast
    img = ImageEnhance.Contrast(img).enhance(image_settings.get("contrast", 1.0))

    # Apply Saturation (Color)
    img = ImageEnhance.Color(img).enhance(image_settings.get("saturation", 1.0))

    # Apply Sharpness
    return ImageEnhance.Sharpness(img).enhance(image_settings.get("sharpness", 1.0))


def compute_image_hash(image):
    """Compute SHA-256 hash of an image."""
    image = image.convert("RGB")
    img_bytes = image.tobytes()
    return hashlib.sha256(img_bytes).hexdigest()


def take_screenshot_html(html_str, dimensions, timeout_ms=None):
    try:
        with tempfile.NamedTemporaryFile(suffix=".html", delete=True) as html_file:
            html_file.write(html_str.encode("utf-8"))
            html_file_path = html_file.name

            return take_screenshot(html_file_path, dimensions, timeout_ms)

    except Exception as e:
        logger.exception(f"Failed to take screenshot: {e!s}")
        return None


def take_screenshot(target, dimensions, timeout_ms=None):
    # Create a temporary output file for the screenshot
    with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as img_file:
        img_file_path = img_file.name

        try:
            command = [
                "chromium-headless-shell",
                target,
                "--headless",
                f"--screenshot={img_file_path}",
                f"--window-size={dimensions[0]},{dimensions[1]}",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--use-gl=swiftshader",
                "--hide-scrollbars",
                "--in-process-gpu",
                "--js-flags=--jitless",
                "--disable-zero-copy",
                "--disable-gpu-memory-buffer-compositor-resources",
                "--disable-extensions",
                "--disable-plugins",
                "--mute-audio",
                "--no-sandbox",
            ]
            if timeout_ms:
                command.append(f"--timeout={timeout_ms}")
            result = subprocess.run(command, capture_output=True)

            # Check if the process failed or the output file is missing
            if result.returncode != 0 or not Path(img_file_path).exists():
                logger.error("Failed to take screenshot:")
                logger.error(result.stderr.decode("utf-8"))
                return None

            # Load the image using PIL
            with Image.open(img_file_path) as img:
                return img.copy()

        except Exception as e:
            logger.exception(f"Failed to take screenshot: {e!s}")
            return None


def pad_image_blur(img: Image.Image, dimensions: tuple[int, int]) -> Image.Image:
    bkg = ImageOps.fit(img, dimensions)
    bkg = bkg.filter(ImageFilter.BoxBlur(8))
    img = ImageOps.contain(img, dimensions)

    img_size = img.size
    bkg.paste(img, ((dimensions[0] - img_size[0]) // 2, (dimensions[1] - img_size[1]) // 2))
    return bkg
