from .datastore.sqla import db
from .babel import babel_init_app
from .template.base import Template
from .email.base import Email
from .usercenter.core import UserCenter
from .security.core import Security
from .admin.admin import Admin
from .views.index.view import IndexView
from .views.user.view import UserView


class Exts:
    """This is used to manager babel,template,admin, and so on..."""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def get_template(self):
        return Template()

    def get_email(self):
        return Email()

    def init_app(self, app):
        self.app = app

        if not hasattr(app, "extensions"):
            app.extensions = {}

        if "exts" in app.extensions:
            raise Exception("exts extension already exists in app.extensions.")

        app.extensions["exts"] = self

        # init sqlalchemy db
        if app.config.get("SQLALCHEMY_DATABASE_URI", None) is None:
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

        if "sqlalchemy" not in app.extensions:
            db.init_app(app)

        # init babel
        if "babel" not in app.extensions:
            babel_init_app(app)

        # init template
        self.template = self.get_template()
        self.template.init_app(app)

        # init email
        self.email = self.get_email()
        self.email.init_app(app)

        # init usercenter and initial login manager in usercenter
        self.usercenter = UserCenter()
        self.usercenter.init_app(app)

        # # init security
        self.security = Security()
        self.security.init_app(app)

        # init admin
        self.admin = Admin()
        self.admin.init_app(app)

        # add default views
        self.admin.add_view(IndexView(), is_menu=False)
        self.admin.add_view(UserView(), is_menu=False)
