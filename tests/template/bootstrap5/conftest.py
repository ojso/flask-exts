import pytest
from flask import Flask
from flask_exts import Manager
from flask_exts.template.theme import Theme
from flask_exts.template.base import Template

class MyTemplate(Template):
     def get_theme(self):
          return Theme()

class MyManager(Manager):
    def get_template(self):
        return MyTemplate()

@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "1"
    manager = MyManager()
    manager.init_app(app)
    yield app
