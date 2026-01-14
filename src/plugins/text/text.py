from plugins.base_plugin.base_plugin import BasePlugin
import logging

logger = logging.getLogger(__name__)


class Text(BasePlugin):
    def generate_settings_template(self):
        template_params = super().generate_settings_template()
        template_params["style_settings"] = True
        return template_params

    def generate_image(self, settings, device_config):
        title = settings.get("title", "")
        content = settings.get("content", "")

        if not content.strip():
            raise RuntimeError("Text content is required.")

        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]

        image_template_params = {
            "title": title,
            "content": content,
            "plugin_settings": settings,
        }

        image = self.render_image(dimensions, "text.html", "text.css", image_template_params)

        return image
