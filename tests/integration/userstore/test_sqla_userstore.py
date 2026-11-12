from datetime import datetime, timedelta

import pytest

from flask_exts.datastore.sqla import db
from flask_exts.userstore.exceptions import (
    AccountLockedError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from flask_exts.userstore.sqla.models import User
from flask_exts.userstore.sqla.userstore import SqlaUserStore


def test_userstore_models_are_registered():
    expected = {"users", "roles", "user_profile", "user_role"}
    assert expected <= set(db.Model.metadata.tables)


def test_base(app):
    us = SqlaUserStore()
    assert us.user_class == User

    with app.app_context():
        db.create_all()
        u1 = us.create_user(username="u1", password="password", email="u1")
        assert u1 is not None
        assert u1.id == 1
        assert u1.username == "u1"

        u2 = us.get_user_by_id(1)
        assert u2.id == 1
        assert u2.username == "u1"

        u3 = us.get_user_by_identity(1)
        assert u3.id == 1
        assert u3.username == "u1"

        us.identity_name = "username"
        u4 = us.get_user_by_identity("u1")
        assert u4.id == 1
        assert u4.username == "u1"

        with pytest.raises(UserAlreadyExistsError, match="username already exists"):
            us.create_user(username="u1", password="password")

        with pytest.raises(UserAlreadyExistsError, match="email already exists"):
            us.create_user(username="u2", password="password", email="u1")

        with pytest.raises(
            InvalidCredentialsError, match="Invalid username or password"
        ):
            us.login_user_by_username_password("missing", "password")

        with pytest.raises(
            InvalidCredentialsError, match="Invalid username or password"
        ):
            us.login_user_by_username_password("u1", "wrong password")


def test_user_roles(app):
    us = SqlaUserStore()
    with app.app_context():
        db.create_all()
        u = us.create_user(username="u1", password="password")
        role_admin = us.create_role("admin")
        role_user = us.create_role("user")

        us.user_add_role(u, role_admin)
        us.user_add_role(u, role_user)

        roles = u.get_roles()
        assert len(roles) == 2
        assert "admin" in roles
        assert "user" in roles


def test_failed_logins_lock_the_account(app):
    us = SqlaUserStore()
    with app.app_context():
        db.create_all()
        us.create_user(username="u1", password="password")

        for _ in range(4):
            with pytest.raises(InvalidCredentialsError):
                us.login_user_by_username_password("u1", "wrong")
        user = us.get_user_by_username("u1")
        assert user.failed_login_count == 4
        assert user.locked_until is None
        assert us.is_locked(user) is False

        with pytest.raises(InvalidCredentialsError):
            us.login_user_by_username_password("u1", "wrong")
        user = us.get_user_by_username("u1")
        assert user.failed_login_count == 5
        assert us.is_locked(user) is True

        with pytest.raises(AccountLockedError, match="Too many failed sign-in"):
            us.login_user_by_username_password("u1", "password")


def test_successful_login_clears_failed_attempts(app):
    us = SqlaUserStore()
    with app.app_context():
        db.create_all()
        us.create_user(username="u1", password="password")

        with pytest.raises(InvalidCredentialsError):
            us.login_user_by_username_password("u1", "wrong")
        user = us.login_user_by_username_password("u1", "password")
        # The counter survives the password step and is cleared only once
        # the whole login flow succeeds.
        assert user.failed_login_count == 1

        us.clear_login_failures(user)
        assert user.failed_login_count == 0
        assert user.locked_until is None


def test_expired_lockout_allows_login(app):
    us = SqlaUserStore()
    with app.app_context():
        db.create_all()
        user = us.create_user(username="u1", password="password")
        us.user_set(
            user,
            failed_login_count=5,
            locked_until=datetime.now() - timedelta(seconds=1),
        )

        assert us.is_locked(user) is False
        assert us.login_user_by_username_password("u1", "password") is not None


def test_lockout_delay_grows_and_is_capped(app):
    us = SqlaUserStore()
    app.config.update(
        USER_LOGIN_MAX_FAILURES=2,
        USER_LOGIN_LOCKOUT_BASE_SECONDS=60,
        USER_LOGIN_LOCKOUT_MAX_SECONDS=300,
    )
    with app.app_context():
        db.create_all()
        user = us.create_user(username="u1", password="password")
        now = datetime(2026, 1, 1, 12, 0, 0)

        assert us.record_login_failure(user, now) is None
        assert us.record_login_failure(user, now) == now + timedelta(seconds=60)
        assert us.record_login_failure(user, now) == now + timedelta(seconds=120)
        assert us.record_login_failure(user, now) == now + timedelta(seconds=240)
        assert us.record_login_failure(user, now) == now + timedelta(seconds=300)
        assert us.record_login_failure(user, now) == now + timedelta(seconds=300)


@pytest.mark.parametrize(
    ("config", "message"),
    [
        ({"USER_LOGIN_MAX_FAILURES": 0}, "USER_LOGIN_MAX_FAILURES"),
        (
            {"USER_LOGIN_LOCKOUT_BASE_SECONDS": 0},
            "USER_LOGIN_LOCKOUT_BASE_SECONDS",
        ),
        (
            {
                "USER_LOGIN_LOCKOUT_BASE_SECONDS": 120,
                "USER_LOGIN_LOCKOUT_MAX_SECONDS": 60,
            },
            "USER_LOGIN_LOCKOUT_MAX_SECONDS",
        ),
    ],
)
def test_invalid_lockout_policy_fails_loudly(app, config, message):
    us = SqlaUserStore()
    app.config.update(config)
    with app.app_context():
        db.create_all()
        user = us.create_user(username="u1", password="password")

        with pytest.raises(ValueError, match=message):
            us.record_login_failure(user)
