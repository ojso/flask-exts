"""Tests for :class:`SimpleAuthorizer`."""

from flask_exts.security.authorizer.simple_authorizer import SimpleAuthorizer


class FakeApp:
    """Only provides the interface needed by ``init_app``."""

    def __init__(self):
        self.config = {}


class MockUser:
    """Mock user for testing the simple authorizer."""

    def __init__(self, roles=None):
        self._roles = roles or []

    def get_roles(self):
        return self._roles

    @property
    def is_anonymous(self):
        return False


class MockUserNoRoles:
    """Mock user without a ``get_roles`` method."""


def make_authorizer():
    authorizer = SimpleAuthorizer()
    authorizer.init_app(FakeApp())
    return authorizer


def _login_required_view():
    def index(self):
        return "index"

    index.__name__ = "index"
    view = type(
        "View",
        (),
        {"allow_access": True, "login_required_functions": ("index",)},
    )()
    return view, index


def test_allow_admin_user():
    authorizer = make_authorizer()
    user = MockUser(roles=["admin"])
    user.is_active = True
    assert authorizer.allow(user=user) is True


def test_deny_inactive_admin_user():
    authorizer = make_authorizer()
    user = MockUser(roles=["admin"])
    user.is_active = False
    assert authorizer.allow(user=user) is False


def test_deny_non_admin_user():
    authorizer = make_authorizer()
    user = MockUser(roles=["editor"])
    assert authorizer.allow(user=user) is False


def test_deny_user_without_roles():
    authorizer = make_authorizer()
    user = MockUser()
    assert authorizer.allow(user=user) is False


def test_deny_no_user():
    authorizer = make_authorizer()
    assert authorizer.allow() is False


def test_view_allow_access_precedes_authentication_gates():
    authorizer = make_authorizer()
    user = MockUser()
    user.is_authenticated = True
    user.is_active = False
    user.tfa_enabled = True

    view = type("View", (), {"allow_access": True})()
    assert authorizer.allow(user=user, view=view) is True


def test_authorize_without_view_uses_permission_context():
    authorizer = make_authorizer()
    user = MockUser(roles=["editor"])

    assert (
        authorizer.authorize(
            user=user,
            resource="/reports",
            method="GET",
            role_need="editor",
        )
        is True
    )
    assert (
        authorizer.authorize(
            user=user,
            resource="/reports",
            method="GET",
        )
        is False
    )


def test_login_required_function_denies_anonymous_despite_allow_access():
    authorizer = make_authorizer()
    view, index = _login_required_view()
    user = MockUser()
    user.is_authenticated = False
    user.is_active = True

    assert authorizer.requires_login(view, index) is True
    assert authorizer.allow(user=user, view=view, fn=index) is False


def test_login_required_function_allows_authenticated_user():
    authorizer = make_authorizer()
    view, index = _login_required_view()
    user = MockUser()
    user.is_authenticated = True
    user.is_active = True

    assert authorizer.allow(user=user, view=view, fn=index) is True


def test_non_public_view_requires_authentication():
    authorizer = make_authorizer()
    view = type("View", (), {"allow_access": False})()
    user = MockUser(roles=["admin"])
    user.is_authenticated = False
    user.is_active = True

    # Role membership must not stand in for a login on a non-public view.
    assert authorizer.allow(user=user, view=view) is False

    user.is_authenticated = True
    assert authorizer.allow(user=user, view=view) is True


def test_view_less_check_falls_back_to_roles():
    authorizer = make_authorizer()
    user = MockUser(roles=["editor"])
    user.is_authenticated = True
    user.is_active = True

    assert authorizer.allow(user=user, role_need="editor") is True
    assert authorizer.allow(user=user, role_need="admin") is False


def test_user_without_get_roles_is_denied():
    authorizer = make_authorizer()
    user = MockUserNoRoles()
    user.is_authenticated = True
    user.is_active = True

    assert authorizer.allow(user=user) is False
