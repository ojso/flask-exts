from flask import url_for
from ..plugin_base import PluginBase


class Select2Plugin(PluginBase):
    def __init__(self):
        super().__init__("select2")

    def style(self):
        url = url_for("_template.static", filename="vendor/select2/select2.min.css")
        return f'<link rel="stylesheet" href="{url}">'

    def script(self):
        url = url_for("_template.static", filename="vendor/select2/select2.min.js")
        return f'<script src="{url}"></script>'
