from flask_login import current_user

from .base import Authorizer


class SimpleAuthorizer(Authorizer):
    """
    Simple Authorizer
    """

    def __init__(self, app=None):
        self.app = None
        self.admin_allow_access = False
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.admin_allow_access = app.config.get("ADMIN_ALLOW_ACCESS", False)

    def authorize(self, *args, **kwargs):
        """
        Authorize access based on user and view.
        """

        if "view" not in kwargs:
            raise ValueError("view is required when SimpleAuthorizer is used.")
        kwargs.setdefault("user", current_user)
        return self.allow(*args, **kwargs)

    def allow(self, *args, **kwargs):
        # Check if the admin_allow_access configuration is set to True
        if self.admin_allow_access:
            return True

        user = kwargs.get("user")

        # Check if the user has the "admin" role, if so, allow access
        if hasattr(user, "get_roles") and "admin" in user.get_roles():
            return True

        view = kwargs.get("view")

        if view is not None and getattr(view, "allow_access", False):
            return True

        # Check if the user is active, if not, deny access
        if not getattr(user, "is_active", True):
            return False

        if (
            "role_need" in kwargs
            and hasattr(user, "get_roles")
            and kwargs["role_need"] in user.get_roles()
        ):
            return True

        return bool(hasattr(user, "get_roles") and "super_admin" in user.get_roles())
