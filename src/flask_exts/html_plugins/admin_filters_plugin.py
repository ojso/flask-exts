from flask import url_for
from .base_plugin import PluginBase


class AdminFiltersPlugin(PluginBase):
    def __init__(self):
        super().__init__("filters")

    def js(self):
        return url_for("_template.static", filename="js/filters.js")
