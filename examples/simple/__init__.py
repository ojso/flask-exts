# app.py
import os.path as op
import textwrap

from flask import Flask

from flask_exts import ExtensionManager
from flask_exts.datastore.sqla import db
from flask_exts.web import View, expose_url


class MockView(View):
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
app.config["SECRET_KEY"] = "change-this-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + op.join(
    op.realpath(op.dirname(__file__)), "app.sqlite"
)

exts = ExtensionManager()
exts.init_app(app)

# Register a mock view
admin = app.extensions["exts"].get_extension("admin").get_admin()
admin.register_view(MockView())

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
