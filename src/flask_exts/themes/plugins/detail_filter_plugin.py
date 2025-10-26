from flask import url_for
from .base_plugin import BasePlugin


class DetailFilterPlugin(BasePlugin):
    def __init__(self):
        super().__init__("detail_filter")

    def js(self):
        return url_for("_template.static", filename="js/detail_filter.js")
