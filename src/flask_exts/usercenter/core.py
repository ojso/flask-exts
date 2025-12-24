from .sqla_user_store import SqlaUserStore


class UserCenter:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.userstore = SqlaUserStore()
