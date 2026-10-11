from flask_exts.security.authorizer.simple_authorizer import SimpleAuthorizer


class FakeApp:
    """Only provides the interface needed by ExtensionManager.init_app."""

    def __init__(self):
        self.config = {}


class MockUser:
    """Mock user for testing authorizer."""

    def __init__(self, roles=None):
        self._roles = roles or []

    def get_roles(self):
        return self._roles

    @property
    def is_anonymous(self):
        return False


class MockUserNoRoles:
    """Mock user without get_roles method."""


class TestSimpleAuthorizer:
    """Test SimpleAuthorizer authorization behavior."""

    def test_allow_admin_user(self):
        authorizer = SimpleAuthorizer()
        authorizer.init_app(FakeApp())
        user = MockUser(roles=["admin"])
        assert authorizer.allow(user=user) is True

    def test_deny_non_admin_user(self):
        authorizer = SimpleAuthorizer()
        user = MockUser(roles=["editor"])
        assert authorizer.allow(user=user) is False

    def test_deny_user_without_roles(self):
        authorizer = SimpleAuthorizer()
        user = MockUser()
        assert authorizer.allow(user=user) is False

    def test_deny_no_user(self):
        authorizer = SimpleAuthorizer()
        assert authorizer.allow() is False

    def test_view_allow_access_precedes_authentication_gates(self):
        authorizer = SimpleAuthorizer()
        authorizer.init_app(FakeApp())
        user = MockUser()
        user.is_authenticated = True
        user.is_active = False
        user.tfa_enabled = True

        view = type("View", (), {"allow_access": True})()
        assert authorizer.allow(user=user, view=view) is True

    def test_admin_allow_access_precedes_authentication_gates(self):
        app = FakeApp()
        app.config["ADMIN_ALLOW_ACCESS"] = True
        authorizer = SimpleAuthorizer(app)
        user = MockUser()
        user.is_authenticated = True
        user.is_active = False
        user.tfa_enabled = True

        assert authorizer.allow(user=user) is True

    def test_authorize_without_view_uses_permission_context(self):
        authorizer = SimpleAuthorizer()
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
