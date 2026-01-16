import logging

from ..base_plugin.base_plugin import BasePlugin
from .github_contributions import contributions_generate_image
from .github_sponsors import sponsors_generate_image
from .github_stars import stars_generate_image

logger = logging.getLogger(__name__)


class GitHub(BasePlugin):
    def generate_settings_template(self):
        template_params = super().generate_settings_template()
        template_params["api_key"] = {
            "required": True,
            "service": "GitHub",
            "expected_key": "GITHUB_SECRET",
        }
        template_params["style_settings"] = True
        return template_params

    def generate_image(self, settings, device_config):
        try:
            github_type = settings.get("githubType", "contributions")

            if github_type == "contributions":
                return contributions_generate_image(self, settings, device_config)
            if github_type == "sponsors":
                return sponsors_generate_image(self, settings, device_config)
            if github_type == "stars":
                return stars_generate_image(self, settings, device_config)
            logger.error(f"Unknown GitHub type: {github_type}")
            msg = f"Unknown GitHub type: {github_type}"
            raise ValueError(msg)
        except Exception as e:
            logger.exception(f"GitHub image generation failed: {e!s}")
            raise
