# simple.py

from flask import Flask
from flask_exts import Manager
from flask_exts.admin import Admin

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"
# Manager init
manager = Manager()
manager.init_app(app)
# Admin init for index_view and user_view
admin = Admin()
admin.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)
