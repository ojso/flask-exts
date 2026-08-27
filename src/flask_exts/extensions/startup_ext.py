from flask import session
from flask_login import user_logged_out
from ..extension.base import Extension
from ..signals import user_registered
from ..proxies import current_security
from ..admin.default_views.index_view import IndexView
from ..usercenter.user_view import UserView


class StartupExtension(Extension):
    @property
    def name(self) -> str:
        return "startup"

    @property
    def priority(self) -> int:
        return 99

    def init_app(self, app):
        """Initialize Jinja2, Flask-Login, subscribe to signals and add admin views."""
        self.subscribe_signals(app)
        self.register_views(app)

    def subscribe_signals(self, app):
        # user registered
        @user_registered.connect_via(app)
        def on_user_registered(sender, user, **extra):
            """Signal handler for user registration."""
            if user.email and not user.email_verified:
                current_security.get_plugin("email_verification").send_token(user)

        # logged out
        @user_logged_out.connect_via(app)
        def on_user_logged_out(sender, user, **extra):
            if "tfa_verified" in session:
                session.pop("tfa_verified")

    def register_views(self, app):
        admin = app.extensions["exts"].get_extension("admin")._admin
        admin.register_view(IndexView(), is_menu=False)
        admin.register_view(UserView(), is_menu=False)
