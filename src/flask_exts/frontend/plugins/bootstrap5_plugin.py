from flask import url_for

from ..plugin_base import PluginBase


class Bootstrap5Plugin(PluginBase):
    def __init__(self):
        super().__init__("bootstrap5")

    def style(self):
        url = url_for(
            "_template.static", filename="vendor/bootstrap5/bootstrap.min.css"
        )
        return f'<link rel="stylesheet" href="{url}">'

    def script(self):
        url = url_for(
            "_template.static", filename="vendor/bootstrap5/bootstrap.bundle.min.js"
        )
        return f'<script src="{url}"></script>'
