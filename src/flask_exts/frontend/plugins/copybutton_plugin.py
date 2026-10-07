from flask import url_for

from ..plugin_base import PluginBase


class CopyButtonPlugin(PluginBase):
    """Plugin for adding copy button functionality to code blocks."""

    def __init__(self):
        super().__init__("copybutton")

    def script(self):
        url = url_for("_template.static", filename="js/copybutton.js")
        return f'<script src="{url}"></script>'
