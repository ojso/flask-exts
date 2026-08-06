from .base import Authorizer

class SimpleAuthorizer(Authorizer):
    """
    Simple Authorizer
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def allow(self, user, resource, method):
        if hasattr(user, "get_roles"):
            if self.root_rolename in user.get_roles():
                return True
        return False

