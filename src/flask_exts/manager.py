from flask_login import LoginManager
from .datastore.sqla import db
from .babel import babel_init_app
from .template.base import Template
from .email.base import Email
from .usercenter.sqla_usercenter import SqlaUserCenter
from .utils.request_user import load_user_from_request
from .security.core import Security


class Manager:
    """This is used to manager babel,template,admin, and so on..."""

    def __init__(self, app=None):
        self.admins = []
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

        if "manager" in app.extensions:
            raise Exception("manager extension already exists in app.extensions.")

        app.extensions["manager"] = self

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

        # init usercenter
        self.usercenter = SqlaUserCenter()

        # login
        if not hasattr(app, "login_manager"):
            login_manager = LoginManager()
            login_manager.init_app(app)
            login_manager.login_view = "user.login"
            # login_manager.login_message = "Please login in"
            login_manager.user_loader(self.usercenter.user_loader)
            login_manager.request_loader(load_user_from_request)

        # init security
        self.security = Security()
        self.security.init_app(app)

        # init admin
        self.admin = self.get_admin_class()()
        self.admin.init_app(app)

    def get_admin_class(self):
        from .admin.base_admin import BaseAdmin

        return BaseAdmin
