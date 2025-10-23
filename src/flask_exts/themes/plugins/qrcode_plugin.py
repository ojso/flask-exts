from flask import url_for
from .base_plugin import BasePlugin


class QRCodePlugin(BasePlugin):
    def __init__(self):
        super().__init__("qrcode")

    def js(self):
        return url_for("_template.static", filename="js/qrcode.js")
