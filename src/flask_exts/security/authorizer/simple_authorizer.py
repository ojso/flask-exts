from flask_login import current_user

from .base import Authorizer


class SimpleAuthorizer(Authorizer):
    """Simple Authorizer"""

    def __init__(self, app=None):
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def authorize(self, *args, **kwargs):
        """Authorize access based on user and optional view or permission context."""

        kwargs.setdefault("user", current_user)
        return self.allow(*args, **kwargs)

    def allow(self, *args, **kwargs):

        user = kwargs.get("user")

        view = kwargs.get("view")

        if view is not None and getattr(view, "allow_access", False):
            return True

        # Disabled accounts lose all authenticated privileges, including admin.
        if not getattr(user, "is_active", True):
            return False

        # Check if the user has the "admin" role, if so, allow access
        if hasattr(user, "get_roles") and "admin" in user.get_roles():
            return True

        if (
            "role_need" in kwargs
            and hasattr(user, "get_roles")
            and kwargs["role_need"] in user.get_roles()
        ):
            return True

        return bool(hasattr(user, "get_roles") and "super_admin" in user.get_roles())
