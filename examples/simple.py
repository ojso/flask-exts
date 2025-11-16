# simple.py

from flask import Flask
from flask import render_template_string
from flask_exts import Exts
from flask_exts.admin import expose
from flask_exts.admin import BaseView
from flask_exts.datastore.sqla import db


class MockView(BaseView):
    @expose("/")
    def index(self):
        return render_template_string(
            "<h1>Mock</h1><div>{{ message }}</div>",
            message="This is mock index view!",
        )


app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"
exts = Exts()
exts.init_app(app)
# Register a mock view
exts.admin.add_view(MockView())

with app.app_context():
    db.drop_all()
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
