from flask_login import current_user

from .base import Authorizer


class SimpleAuthorizer(Authorizer):
    """
    Simple Authorizer
    """

    def __init__(self, app=None):
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def authorize(self, *args, **kwargs):
        """
        Authorize access based on user and optional view or permission context.
        """

        kwargs.setdefault("user", current_user)
        return self.allow(*args, **kwargs)

    def allow(self, *args, **kwargs):

        user = kwargs.get("user")

        # Check if the user has the "admin" role, if so, allow access
        if hasattr(user, "get_roles") and "admin" in user.get_roles():
            return True

        view = kwargs.get("view")
        fn = kwargs.get("fn")

        # @requires_active marks a specific method as an account-authenticated
        # feature (change password, enable TFA, ...) rather than a genuinely
        # public endpoint, even on a view class that otherwise sets
        # allow_access = True for its public endpoints (login, register, ...).
        # A disabled (is_active=False) account's still-valid session must not
        # be able to use it -- but once active, it should still get the same
        # free pass allow_access gives everyone else, not fall through to the
        # admin/super_admin-only checks below (those are for admin RBAC, not
        # for a user managing their own account).
        if getattr(fn, "_requires_active", False) and not getattr(
            user, "is_active", True
        ):
            return False

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
