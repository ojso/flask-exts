# simple.py
import os.path as op
from flask import Flask
from flask_exts import Exts
from flask_exts.admin import expose_url
from flask_exts.admin import View
from flask_exts.datastore.sqla import db


class MockView(View):
    @expose_url("/")
    def index(self):
        s = '''
            {% extends "admin/master.html" %}
            {% block title %}Mock View{% endblock %}
            {% block main %}
                <h1>Mock View</h1>
                <div>This is a simple mock view for demonstration purposes.</div>
            {% endblock %}
        '''
        return self.render_string(s)


app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"
# app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + op.join(
    op.realpath(op.dirname(__file__)), "simple.sqlite"
)
exts = Exts()
exts.init_app(app)
# Register a mock view
exts.admin.add_view(MockView())

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
