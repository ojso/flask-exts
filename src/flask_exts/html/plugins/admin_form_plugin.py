from flask import url_for
from ..plugin_base import PluginBase


class AdminFormPlugin(PluginBase):
    def __init__(self):
        super().__init__("form")

    def script(self):
        url = url_for("_template.static", filename="js/form.js")
        return f'<script src="{url}"></script>'
