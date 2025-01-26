from flask import Flask
from flask_exts import Manager
from flask_exts.admin import Admin
from flask_exts.admin import BaseView
from flask_exts.admin import expose

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"
manager = Manager()
manager.init_app(app)


class FirstView(BaseView):
    @expose("/")
    def index(self):
        return self.render("first.html")


class SecondView(BaseView):
    @expose("/")
    def index(self):
        return self.render("second.html")


admin1 = Admin(app, url="/admin1",endpoint="admin1")
admin1.add_view(FirstView())

# Create second administrative interface under /admin2
admin2 = Admin(app, url="/admin2", endpoint="admin2")
admin2.add_view(SecondView())


if __name__ == "__main__":
    app.run(debug=True)
