from flask import url_for
from .base_plugin import BasePlugin


class Bootstrap4Plugin(BasePlugin):
    def __init__(self):
        super().__init__("bootstrap4")

    def css(self):
        return url_for(
            "_template.static", filename="vendor/bootstrap4/bootstrap.min.css"
        )

    def js(self):
        return url_for(
            "_template.static", filename="vendor/bootstrap4/bootstrap.bundle.min.js"
        )
