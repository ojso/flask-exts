from flask_login import LoginManager

login_manager = LoginManager()


def default_user_loader(user_id):
    return None


def login_init_app(app):
    login_manager.init_app(app)
    login_manager.user_loader(default_user_loader)

    return login_manager
