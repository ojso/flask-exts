from flask import url_for
from .base_plugin import BasePlugin


class ClipboardPlugin(BasePlugin):
    def __init__(self):
        super().__init__("clipboard")

    def js(self):
        return url_for("_template.static", filename="vendor/clipboard/clipboard.min.js")
