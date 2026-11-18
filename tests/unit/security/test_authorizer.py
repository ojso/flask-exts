"""Tests for the shared :class:`Authorizer` behaviour."""

from flask_exts.security.authorizer.base import Authorizer


class DummyAuthorizer(Authorizer):
    """Concrete authorizer used to exercise the base helpers."""

    def __init__(self):
        self.seen = None

    def allow(self, *args, **kwargs):
        self.seen = kwargs.get("user")
        return True


class User:
    """Minimal user implementing the attributes the base helpers read."""

    def __init__(self, roles=(), is_active=True, is_authenticated=True):
        self.roles = list(roles)
        self.is_active = is_active
        self.is_authenticated = is_authenticated

    def get_roles(self):
        return self.roles


class UserWithoutRoles:
    """User without the optional ``get_roles`` method."""

    is_active = True
    is_authenticated = True


def make_view(**attrs):
    return type("View", (), attrs)()


def make_function(name="other"):
    def func(self):
        return name

    func.__name__ = name
    return func


def test_check_view_access_without_view_has_no_decision():
    authorizer = DummyAuthorizer()
    assert authorizer.check_view_access(User(), None) is None


def test_public_view_allows_anonymous_unlisted_method():
    authorizer = DummyAuthorizer()
    view = make_view(allow_access=True, login_required_functions=("index",))

    assert (
        authorizer.check_view_access(
            User(is_authenticated=False), view, make_function()
        )
        is True
    )


def test_public_view_denies_anonymous_listed_method():
    authorizer = DummyAuthorizer()
    view = make_view(allow_access=True, login_required_functions=("index",))

    assert (
        authorizer.check_view_access(
            User(is_authenticated=False), view, make_function("index")
        )
        is False
    )


def test_public_view_allows_authenticated_listed_method():
    authorizer = DummyAuthorizer()
    view = make_view(allow_access=True, login_required_functions=("index",))

    assert authorizer.check_view_access(User(), view, make_function("index")) is True


def test_non_public_view_denies_anonymous_user():
    authorizer = DummyAuthorizer()
    view = make_view(allow_access=False)

    assert authorizer.check_view_access(User(is_authenticated=False), view) is False


def test_non_public_view_defers_for_authenticated_user():
    authorizer = DummyAuthorizer()
    view = make_view(allow_access=False)

    assert authorizer.check_view_access(User(), view) is None


def test_admin_role_passes_the_shared_gate():
    authorizer = DummyAuthorizer()
    view = make_view(allow_access=False)

    assert authorizer.check_view_access(User(["admin"]), view) is True


def test_inactive_admin_does_not_use_the_superuser_shortcut():
    authorizer = DummyAuthorizer()
    view = make_view(allow_access=False)

    assert authorizer.check_view_access(User(["admin"], is_active=False), view) is None


def test_anonymous_admin_role_is_denied_on_non_public_view():
    authorizer = DummyAuthorizer()
    view = make_view(allow_access=False)

    assert (
        authorizer.check_view_access(User(["admin"], is_authenticated=False), view)
        is False
    )


def test_requires_login_matches_the_function_name():
    authorizer = DummyAuthorizer()
    view = make_view(login_required_functions=("index",))

    assert authorizer.requires_login(view, make_function("index")) is True
    assert authorizer.requires_login(view, make_function("other")) is False


def test_requires_login_ignores_missing_view_and_function():
    authorizer = DummyAuthorizer()
    view = make_view(login_required_functions=("index",))

    assert authorizer.requires_login(None, make_function("index")) is False
    assert authorizer.requires_login(view, None) is False
    assert authorizer.requires_login(view, "index") is False


def test_allow_by_roles_denies_inactive_user():
    authorizer = DummyAuthorizer()

    assert authorizer.allow_by_roles(User(["admin"], is_active=False)) is False


def test_allow_by_roles_allows_admin():
    authorizer = DummyAuthorizer()

    assert authorizer.allow_by_roles(User(["admin"])) is True


def test_allow_by_roles_allows_role_need():
    authorizer = DummyAuthorizer()

    assert authorizer.allow_by_roles(User(["editor"]), role_need="editor") is True


def test_allow_by_roles_denies_user_without_roles():
    authorizer = DummyAuthorizer()

    assert authorizer.allow_by_roles(User()) is False
    assert authorizer.allow_by_roles(UserWithoutRoles()) is False


def test_authorize_passes_the_given_user_to_allow():
    authorizer = DummyAuthorizer()
    user = User()

    assert authorizer.authorize(user=user) is True
    assert authorizer.seen is user
