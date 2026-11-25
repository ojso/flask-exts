from abc import ABC, abstractmethod

from flask_login import current_user

SESSION_KEY_TFA_VERIFIED = "tfa_verified"
SESSION_KEY_TFA_RECOVERY = "tfa_recovery_login"

#: Holds the id of a user who passed the password check but, because their
#: account has TFA enabled, has not yet completed the TFA step. No login
#: session exists for this user until TFA verification succeeds -- Flask-Login's
#: `login_user` is deliberately not called until then. If the browser leaves
#: this page (closes, lets the session expire, etc.) the pending login is
#: simply abandoned; the user must restart from username/password.
SESSION_KEY_PENDING_TFA_USER_ID = "pending_tfa_user_id"


class Authorizer(ABC):
    """Base class for access-control implementations."""

    @abstractmethod
    def allow(self, *args, **kwargs): ...

    def authorize_object(self, view, fn, obj, requirement):
        """Authorize a single object for an exposed view method.

        Args:
            view: The admin view instance owning the object.
            fn: The exposed view method being called.
            obj: The model object the request resolved to.
            requirement: Object-level requirement to evaluate.

        Returns:
            bool: ``True`` when the object may be accessed. The default
                implementation fails closed; authorizers that support
                object-level requirements must override it.
        """
        return False

    def authorize(self, *args, **kwargs):
        """Authorize access using the current user unless one is provided."""
        kwargs.setdefault("user", current_user)
        return self.allow(*args, **kwargs)

    @staticmethod
    def requires_login(view, fn):
        """Return whether ``fn`` is declared as login-required on ``view``.

        Args:
            view: The admin view instance, when the check comes from a view.
            fn: The view function being called, when known.

        Returns:
            bool: ``True`` when ``fn`` is named in
                ``view.login_required_functions``.
        """
        if view is None or not callable(fn):
            return False
        names = getattr(view, "login_required_functions", ())
        return getattr(fn, "__name__", None) in names

    def check_view_access(self, user, view, fn=None):
        """Apply the login gate shared by the built-in authorizers.

        The rule depends on the view's ``allow_access`` flag and the methods
        named in ``login_required_functions``, plus one shared superuser rule:
        an authenticated, active user with the ``admin`` role passes every
        view without evaluating further requirements. Every authorizer must
        apply this gate before its own role, permission or predicate checks.

        Args:
            user: The user the check applies to.
            view: The admin view instance, or ``None`` when the check does
                not come from a view.
            fn: The view function being called, when known.

        Returns:
            bool | None: ``False`` when access is denied because a logged-in
                user is required. ``True`` when the active ``admin`` role or a
                public view (``allow_access=True``) already grants access.
                ``None`` when there is no view-level decision and the caller
                should keep authorizing.
        """
        if view is None:
            return None

        authenticated = bool(getattr(user, "is_authenticated", False))

        if authenticated and getattr(user, "is_active", True):
            get_roles = getattr(user, "get_roles", None)
            if callable(get_roles) and "admin" in get_roles():
                # The admin role is a superuser: it passes every view without
                # evaluating role, permission or predicate requirements.
                return True

        if getattr(view, "allow_access", False):
            # Public view: only the methods named in
            # ``login_required_functions`` need a logged-in user.
            return not (self.requires_login(view, fn) and not authenticated)

        # Non-public views always require a logged-in user.
        return None if authenticated else False

    @staticmethod
    def allow_by_roles(user, **kwargs):
        """Apply the role fallback shared by the built-in authorizers.

        Args:
            user: The user the check applies to.
            **kwargs: Extra authorization data; ``role_need`` is matched
                against the user's roles.

        Returns:
            bool: ``True`` when an active admin or the requested role grants
                access.
        """
        if not getattr(user, "is_active", True):
            return False

        if hasattr(user, "get_roles") and "admin" in user.get_roles():
            return True

        if "role_need" not in kwargs or not hasattr(user, "get_roles"):
            return False

        return kwargs["role_need"] in user.get_roles()
