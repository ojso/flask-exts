from flask import url_for
from ..plugin_base import PluginBase


class ClipboardPlugin(PluginBase):
    def __init__(self):
        super().__init__("clipboard")

    def script(self):
        url = url_for("_template.static", filename="vendor/clipboard/clipboard.min.js")
        return f'<script src="{url}"></script>'
