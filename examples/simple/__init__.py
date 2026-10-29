# app.py
import textwrap

from flask import Flask

from flask_exts import ExtensionManager
from flask_exts.admin import View, expose_url
from flask_exts.datastore.sqla import db


class MockView(View):
    allow_access = True

    @expose_url("/")
    def index(self):
        s = textwrap.dedent("""
        {% extends "admin/master.html" %}
        {% block title %}Mock View{% endblock %}
        {% block main %}
            <h1>Mock View</h1>
            <div>This is a simple mock view for demonstration purposes.</div>
        {% endblock %}
        """).strip()
        return self.render_string(s)


app = Flask(__name__)
app.config["SECRET_KEY"] = "simple"
app.config["APP_NAME"] = "FlaskSimple"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
exts = ExtensionManager()
exts.init_app(app)

# Register a mock view
admin = app.extensions["exts"].get_extension("admin").get_admin()
admin.register_view(MockView())

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
