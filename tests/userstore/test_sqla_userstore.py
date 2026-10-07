import pytest

from flask_exts.datastore.sqla import db
from flask_exts.userstore.exceptions import (
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
