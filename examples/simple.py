# simple.py
import os.path as op
from flask import Flask
from flask import render_template_string
from flask_exts import Exts
from flask_exts.admin import expose_url
from flask_exts.admin import View
from flask_exts.datastore.sqla import db

def get_sqlite_path():
    app_dir = op.realpath(op.dirname(__file__))
    database_path = op.join(app_dir, "simple.sqlite")
    return database_path

class MockView(View):
    @expose_url("/")
    def index(self):
        print(db.engine)
        # return "123"
        return render_template_string(
            "<h1>Mock</h1><div>{{ message }}</div>",
            message="This is mock index view!",
        )


app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"
# app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + get_sqlite_path()
exts = Exts()
exts.init_app(app)
# Register a mock view
exts.admin.add_view(MockView())

with app.app_context():
    print(db.engine)
    db.drop_all()
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
