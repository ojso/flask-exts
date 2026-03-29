from flask import url_for
from .base_plugin import PluginBase


class DaterangepickerPlugin(PluginBase):
    def __init__(self):
        super().__init__("daterangepicker")

    def css(self):
        return url_for(
            "_template.static", filename="vendor/daterangepicker/daterangepicker.css"
        )

    def js(self):
        return url_for(
            "_template.static", filename="vendor/daterangepicker/daterangepicker.js"
        )
