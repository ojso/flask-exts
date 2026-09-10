from flask import url_for
from ..plugin_base import PluginBase


class MomentPlugin(PluginBase):
    def __init__(self):
        super().__init__("moment", weight=90)

    def script(self):
        url = url_for("_template.static", filename="vendor/moment.min.js")
        return f'<script src="{url}"></script>'
