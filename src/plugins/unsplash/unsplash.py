import logging
import random
from io import BytesIO

import requests
from PIL import Image

from plugins.base_plugin.base_plugin import BasePlugin

logger = logging.getLogger(__name__)


def grab_image(image_url, dimensions, timeout_ms=40000):
    """Grab an image from a URL and resize it to the specified dimensions."""
    try:
        response = requests.get(image_url, timeout=timeout_ms / 1000)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img.resize(dimensions, Image.Resampling.LANCZOS)
    except Exception as e:
        logger.exception(f"Error grabbing image from {image_url}: {e}")
        return None


class Unsplash(BasePlugin):
    def generate_image(self, settings, device_config):
        access_key = device_config.load_env_key("UNSPLASH_ACCESS_KEY")
        if not access_key:
            msg = "'Unsplash Access Key' not found."
            raise RuntimeError(msg)

        search_query = settings.get("search_query")
        collections = settings.get("collections")
        content_filter = settings.get("content_filter", "low")
        color = settings.get("color")
        orientation = settings.get("orientation")

        params = {
            "client_id": access_key,
            "content_filter": content_filter,
            "per_page": 100,
        }

        if search_query:
            url = "https://api.unsplash.com/search/photos"
            params["query"] = search_query
        else:
            url = "https://api.unsplash.com/photos/random"

        if collections:
            params["collections"] = collections
        if color:
            params["color"] = color
        if orientation:
            params["orientation"] = orientation

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if search_query:
                results = data.get("results")
                if not results:
                    msg = "No images found for the given search query."
                    raise RuntimeError(msg)
                image_url = random.choice(results)["urls"]["full"]
            else:
                image_url = data["urls"]["full"]
        except requests.exceptions.RequestException as e:
            logger.exception(f"Error fetching image from Unsplash API: {e}")
            msg = "Failed to fetch image from Unsplash API, please check logs."
            raise RuntimeError(msg)
        except (KeyError, IndexError) as e:
            logger.exception(f"Error parsing Unsplash API response: {e}")
            msg = "Failed to parse Unsplash API response, please check logs."
            raise RuntimeError(msg)

        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]

        logger.info(f"Grabbing image from: {image_url}")

        image = grab_image(image_url, dimensions, timeout_ms=40000)

        if not image:
            msg = "Failed to load image, please check logs."
            raise RuntimeError(msg)

        return image
