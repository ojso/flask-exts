import pytest
from flask_exts.security.authorizer.base import Authorizer
from flask_exts.security.authorizer.simple_authorizer import SimpleAuthorizer


class MockUser:
    """Mock user for testing authorizer."""

    def __init__(self, roles=None):
        self._roles = roles or []

    def get_roles(self):
        return self._roles


class MockUserNoRoles:
    """Mock user without get_roles method."""
    pass


class TestAuthorizerBase:
    """Test the Authorizer base class."""

    def test_is_root_user_with_admin_role(self):
        authorizer = SimpleAuthorizer()
        user = MockUser(roles=["admin"])
        assert authorizer.is_root_user(user) is True

    def test_is_root_user_without_admin_role(self):
        authorizer = SimpleAuthorizer()
        user = MockUser(roles=["editor", "viewer"])
        assert authorizer.is_root_user(user) is False

    def test_is_root_user_empty_roles(self):
        authorizer = SimpleAuthorizer()
        user = MockUser(roles=[])
        assert authorizer.is_root_user(user) is False

    def test_is_root_user_no_roles_method(self):
        authorizer = SimpleAuthorizer()
        user = MockUserNoRoles()
        assert authorizer.is_root_user(user) is False

    def test_is_root_user_none(self):
        authorizer = SimpleAuthorizer()
        assert authorizer.is_root_user(None) is False

    def test_set_root_rolename(self):
        authorizer = SimpleAuthorizer()
        authorizer.set_root_rolename("superadmin")
        assert authorizer.root_rolename == "superadmin"

        user = MockUser(roles=["superadmin"])
        assert authorizer.is_root_user(user) is True

        user_admin = MockUser(roles=["admin"])
        assert authorizer.is_root_user(user_admin) is False

    def test_default_root_rolename(self):
        authorizer = SimpleAuthorizer()
        assert authorizer.root_rolename == "admin"


class TestSimpleAuthorizer:
    """Test SimpleAuthorizer.allow() method."""

    def test_allow_admin_user(self):
        authorizer = SimpleAuthorizer()
        user = MockUser(roles=["admin"])
        assert authorizer.allow(user, "any_resource", "GET") is True
        assert authorizer.allow(user, "any_resource", "POST") is True
        assert authorizer.allow(user, "any_resource", "DELETE") is True

    def test_deny_non_admin_user(self):
        authorizer = SimpleAuthorizer()
        user = MockUser(roles=["editor"])
        assert authorizer.allow(user, "any_resource", "GET") is False

    def test_deny_user_without_roles(self):
        authorizer = SimpleAuthorizer()
        user = MockUser(roles=[])
        assert authorizer.allow(user, "any_resource", "GET") is False

    def test_deny_user_no_get_roles(self):
        authorizer = SimpleAuthorizer()
        user = MockUserNoRoles()
        assert authorizer.allow(user, "any_resource", "GET") is False

    def test_allow_with_custom_root_role(self):
        authorizer = SimpleAuthorizer()
        authorizer.set_root_rolename("superuser")
        user = MockUser(roles=["superuser"])
        assert authorizer.allow(user, "resource", "GET") is True

    def test_deny_old_admin_after_role_change(self):
        authorizer = SimpleAuthorizer()
        authorizer.set_root_rolename("superuser")
        user = MockUser(roles=["admin"])
        assert authorizer.allow(user, "resource", "GET") is False

    def test_init_app(self):
        """Test init_app doesn't raise."""
        from flask import Flask

        app = Flask(__name__)
        authorizer = SimpleAuthorizer()
        authorizer.init_app(app)
        assert authorizer.app is app

    def test_init_with_app(self):
        """Test constructor with app parameter."""
        from flask import Flask

        app = Flask(__name__)
        authorizer = SimpleAuthorizer(app)
        assert authorizer.app is app
