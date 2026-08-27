from flask import url_for
from ..plugin_base import PluginBase


class AdminFormPlugin(PluginBase):
    def __init__(self):
        super().__init__("form")

    def js(self):
        return url_for("_template.static", filename="js/form.js")
