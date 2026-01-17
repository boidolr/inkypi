import logging
import random

from plugins.base_plugin.base_plugin import BasePlugin

logger = logging.getLogger(__name__)


class Text(BasePlugin):
    def generate_settings_template(self):
        template_params = super().generate_settings_template()
        template_params["style_settings"] = True
        return template_params

    def generate_image(self, settings, device_config):
        title = settings.get("title", "")
        text_entries = settings.get("text-entries[]", [])

        if not text_entries or not any(entry.strip() for entry in text_entries):
            msg = "At least one text entry is required."
            raise RuntimeError(msg)

        # Filter out empty entries
        valid_entries = [entry for entry in text_entries if entry.strip()]

        # Randomly select one entry
        content = random.choice(valid_entries)

        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]

        image_template_params = {
            "title": title,
            "content": content,
            "plugin_settings": settings,
        }

        return self.render_image(dimensions, "text.html", "text.css", image_template_params)
