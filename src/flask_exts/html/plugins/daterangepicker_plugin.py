from flask import url_for
from ..plugin_base import PluginBase


class DaterangepickerPlugin(PluginBase):
    def __init__(self):
        super().__init__("daterangepicker")

    def style(self):
        url = url_for(
            "_template.static", filename="vendor/daterangepicker/daterangepicker.css"
        )
        return f'<link rel="stylesheet" href="{url}">'

    def js(self):
        url = url_for(
            "_template.static", filename="vendor/daterangepicker/daterangepicker.js"
        )
        return f'<script src="{url}"></script>'
