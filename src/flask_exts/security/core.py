from .authorize import CasbinEnforcer


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
        app.extensions["security"] = self
        self.casbin = CasbinEnforcer(app)
