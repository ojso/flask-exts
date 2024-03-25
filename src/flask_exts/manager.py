from .babel.babel_setting import flask_babel_init_app


class Manager:
    """This is used to manager babel,form,admin."""

    def init_flask_babel(self,app):
        flask_babel_init_app(app)

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

        if not hasattr(app, "extensions"):
            app.extensions = {}

        app.extensions["manager"] = self

        if 'babel' not in app.extensions:
            self.init_flask_babel(app)
