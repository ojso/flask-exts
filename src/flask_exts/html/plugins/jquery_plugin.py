from flask import url_for
from ..plugin_base import PluginBase


class jQueryPlugin(PluginBase):
    def __init__(self):
        super().__init__("jquery", weight=99)

    def script(self):
        url = url_for("_template.static", filename="vendor/jquery/jquery.min.js")
        return f'<script src="{url}"></script>'
