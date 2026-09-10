from flask import url_for
from ..plugin_base import PluginBase


class Bootstrap4Plugin(PluginBase):
    def __init__(self):
        super().__init__("bootstrap4", weight=90)

    def style(self):
        url = url_for(
            "_template.static", filename="vendor/bootstrap4/bootstrap.min.css"
        )
        return f'<link rel="stylesheet" href="{url}">'

    def script(self):
        url = url_for(
            "_template.static", filename="vendor/bootstrap4/bootstrap.bundle.min.js"
        )
        return f'<script src="{url}"></script>'
