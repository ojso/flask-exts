from flask_login import LoginManager
from .usercenter.sqla_usercenter import SqlaUserCenter
from .usercenter.memory_usercenter import MemoryUserCenter
from .authorize import CasbinAuthorizer
from ..utils.request_user import load_user_from_request


class Security:
    def __init__(
        self,
        app=None,
    ):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(
        self,
        app,
    ):
        self.app = app

        # usercenter
        if "SQLALCHEMY_USERCENTER" in app.config:
            self.usercenter = SqlaUserCenter()
        else:
            self.usercenter = MemoryUserCenter()

        # login
        if not hasattr(app, "login_manager"):
            login_manager = LoginManager()
            login_manager.init_app(app)
            login_manager.login_view = self.usercenter.login_view
            # login_manager.login_message = "Please login in"
            login_manager.user_loader(self.usercenter.user_loader)
            login_manager.request_loader(load_user_from_request)

        # authorizer
        self.authorizer = CasbinAuthorizer(app)

        # set extension
        app.extensions["security"] = self

