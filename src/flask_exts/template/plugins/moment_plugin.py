from flask import url_for
from .base_plugin import PluginBase


class MomentPlugin(PluginBase):
    def __init__(self):
        super().__init__("moment")

    def js(self):
        return url_for("_template.static", filename="vendor/moment.min.js")
