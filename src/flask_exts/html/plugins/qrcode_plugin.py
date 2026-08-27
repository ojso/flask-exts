from flask import url_for
from ..plugin_base import PluginBase


class QRCodePlugin(PluginBase):
    def __init__(self):
        super().__init__("qrcode")

    def js(self):
        return url_for("_template.static", filename="js/qrcode.js")
