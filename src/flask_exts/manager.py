from .babel import babel_init_app
from .templating import template_init_app
from .login import login_init_app


class Manager:
    """This is used to manager babel,form,admin."""

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

        if not hasattr(app, "extensions"):
            app.extensions = {}

        if app.config.get("BABEL_ENABLED", True) and "babel" not in app.extensions:
            babel_init_app(app)

        if (
            app.config.get("TEMPLATE_ENABLED", True)
            and "template" not in app.extensions
        ):
            template_init_app(app=app)

        if app.config.get("FLASK_LOGIN_ENABLED", True) and getattr(app,"login_manager",None) is None:
            self.login_manager = login_init_app(app)
