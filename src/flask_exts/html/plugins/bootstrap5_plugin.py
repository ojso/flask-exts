from flask import url_for
from ..plugin_base import PluginBase


class Bootstrap5Plugin(PluginBase):
    def __init__(self):
        super().__init__("bootstrap5")

    def css(self):
        return url_for(
            "_template.static", filename="vendor/bootstrap5/bootstrap.min.css"
        )

    def js(self):
        return url_for(
            "_template.static", filename="vendor/bootstrap5/bootstrap.bundle.min.js"
        )
