from flask import url_for

from ..plugin_base import PluginBase


class AdminFiltersPlugin(PluginBase):
    def __init__(self):
        super().__init__("filters")

    def script(self):
        url = url_for("_template.static", filename="js/filters.js")
        return f'<script src="{url}"></script>'
