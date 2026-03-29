from flask import url_for
from .base_plugin import PluginBase


class Select2Plugin(PluginBase):
    def __init__(self):
        super().__init__("select2")

    def css(self):
        return url_for("_template.static", filename="vendor/select2/select2.min.css")

    def js(self):
        return url_for("_template.static", filename="vendor/select2/select2.min.js")
