from flask import url_for
from markupsafe import Markup

class Plugin:
    def __init__(self):
        self.names = []

    def enable(self, name):
        if name not in self.names:
            self.names.append(name)

    def load_js(self, name):
        match name:
            case "qrcode":
                js= f'<script src="{ url_for("template.static",filename="js/qrcode.js") }"></script>'
            case _:
                js = ""
        return Markup(js)
