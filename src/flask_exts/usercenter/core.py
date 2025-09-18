from flask import session
from flask_login import LoginManager
from flask_login import user_logged_out
from .sqla_user_store import SqlaUserStore
from ..proxies import _security
from ..utils.request_user import load_user_from_request
from ..signals import user_registered


class UserCenter:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.userstore = SqlaUserStore()
        self.init_login(app)
        self.subscribe_signal(app)

    def subscribe_signal(self, app):
        user_registered.connect(self.after_user_registered, app)

    def after_user_registered(self, sender, user, **kwargs):
        """Signal handler for user registration."""
        if user.email and not user.email_verified:
            _security.email_verification.send_verify_email_token(user)

    def init_login(self, app):
        if not hasattr(app, "login_manager"):
            login_manager = LoginManager()
            login_manager.init_app(app)
            login_manager.login_view = "user.login"
            # login_manager.login_message = "Please login in"
            login_manager.user_loader(self.userstore.user_loader)
            login_manager.request_loader(load_user_from_request)

        @user_logged_out.connect_via(app)
        def on_user_logged_out(sender, user):
            if "tfa_verified" in session:
                session.pop("tfa_verified")

