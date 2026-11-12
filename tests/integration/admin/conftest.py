import pytest

from flask_exts.datastore.sqla import db
from flask_exts.proxies import current_userstore


@pytest.fixture
def admin(app):
    return app.extensions["exts"].get_extension("admin").get_admin()


def _create_admin_user():
    """Create (within an active app context) a persisted, active user with
    the "admin" role.
    """
    user = current_userstore.create_user(
        username="admin_test_user",
        password="admin_test_password",
        email="admin_test_user@example.com",
    )
    role = current_userstore.create_role("admin")
    current_userstore.user_add_role(user, role)
    return user


@pytest.fixture
def login_as_admin(app, client):
    """Factory fixture: call login_as_admin() to log `client` in as a fresh
    admin-role user.

    This is a callable rather than a plain value because most tests under
    tests/integration/admin/ start their body with `db.reset_all()`, which would wipe
    out a user created ahead of time by a regular fixture. Call this *after*
    resetting the database, inside the test's own `app.app_context()`::

        def test_something(app, client, admin, login_as_admin):
            with app.app_context():
                db.reset_all()
                login_as_admin()
                ...
    """

    def _login():
        db.create_all()  # no-op if tables already exist (e.g. after reset_all())
        user = _create_admin_user()
        with client.session_transaction() as sess:
            sess["_user_id"] = user.get_id()
            sess["_fresh"] = True
        return user

    return _login
