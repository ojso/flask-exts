from flask_login import LoginManager
from .user_center import DefaultUserCenter


def user_init_app(app):
    user_center = app.config.get("USER_CENTER") or DefaultUserCenter()
    app.extensions["usercenter"] = user_center

    if app.config.get("FLASK_LOGIN_ENABLED", True) and not hasattr(
        app, "login_manager"
    ):
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = user_center.login_view
        login_manager.user_loader(user_center.user_loader)
