from .base import Authorizer


class SimpleAuthorizer(Authorizer):
    """Simple Authorizer"""

    def __init__(self, app=None):
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def allow(self, *args, **kwargs):
        user = kwargs.get("user")
        decision = self.check_view_access(user, kwargs.get("view"), kwargs.get("fn"))
        if decision is not None:
            return decision

        # Without a view there is nothing to authorize against; fall back to
        # the role rules used by API-style callers.
        return self.allow_by_roles(**{**kwargs, "user": user})
