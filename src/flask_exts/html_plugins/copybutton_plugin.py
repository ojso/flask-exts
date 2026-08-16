from flask import url_for
from .base_plugin import PluginBase


class CopyButtonPlugin(PluginBase):
    """Plugin for adding copy button functionality to code blocks."""

    def __init__(self):
        super().__init__("copybutton")

    def js(self):
        return url_for("_template.static", filename="js/copybutton.js")
