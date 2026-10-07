import pytest

from flask_exts.builtin_extensions.login_ext import user_loader
from flask_exts.datastore.sqla import db
from flask_exts.proxies import current_security, current_userstore
from flask_exts.security.exceptions import (
    InvalidTokenError,
    MissingPasswordError,
)
from flask_exts.security.keys import derive_key


class TestSecurity:
    def test_security_keys_are_derived_per_purpose(self, app):
        with app.app_context():
            master_key = app.secret_key
            master_key_bytes = (
                master_key.encode("utf-8")
                if isinstance(master_key, str)
                else master_key
            )
            hasher_key = current_security.hasher.key
            serializer_key = current_security.serializer.key

            assert hasher_key == derive_key(master_key, "hasher")
            assert serializer_key == derive_key(master_key, "url-token")
            assert hasher_key != serializer_key
            assert hasher_key != master_key_bytes
            assert serializer_key != master_key_bytes

    def test_hasher(self, app):
        with app.app_context():
            security_hasher = current_security.hasher
            data1 = "test"
            data2 = "test"
            h1 = security_hasher.hash(data1)
            r = security_hasher.verify(data2, h1)
            assert r is True

    def test_serializer(self, app):
        with app.app_context():
            security_serializer = current_security.serializer
            data = {"test": "data"}
            token = security_serializer.dumps("test", data)
            assert token is not None
            r = security_serializer.loads("test", token, max_age=3600)
            # print(r)
            assert r[0] is False
            assert r[1] is False
            assert r[2] == data
            # import time
            # time.sleep(3)
            # r = security_serializer.loads("test", token, max_age=2)
            # print(r)
            # assert r[0] is True
            # assert r[1] is False
            # assert r[2] == data

    def test_verify_email(self, app):
        with app.app_context():
            db.reset_all()
            user = current_userstore.create_user(
                username="testuser",
                password="testpassword",
                email="testuser@example.com",
            )
            assert user is not None
            assert user.is_active is False
            ev = current_security.get_plugin("email_verification")
            token = ev.generate_token(user)
            r = ev.execute_with_token(token)
            assert r == "verified"
            assert user.email_verified is True
            assert user.is_active is True

            with pytest.raises(InvalidTokenError):
                ev.execute_with_token("invalid-token")

            reset_password = current_security.get_plugin("reset_password")
            reset_token = reset_password.generate_token(user)
            with pytest.raises(MissingPasswordError):
                reset_password.execute_with_token(reset_token, password="")

            assert current_security.get_within("reset_password") == 1800
            reset_password.execute_with_token(
                reset_token, password="new-test-password"
            )
            with pytest.raises(InvalidTokenError):
                reset_password.execute_with_token(
                    reset_token, password="another-test-password"
                )

    def test_password_change_invalidates_existing_login_session(self, app):
        with app.app_context():
            db.reset_all()
            user = current_userstore.create_user(
                username="session-user",
                password="session-password",
                email="session-user@example.com",
            )
            current_userstore.user_set(user, is_active=True)
            old_session_user_id = user.get_id()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["_user_id"] = old_session_user_id
                sess["_fresh"] = True

            with app.app_context():
                user = current_userstore.user_loader(user.id)
                current_userstore.user_set(
                    user, password=user.hash_password("new-session-password")
                )
                assert user_loader(old_session_user_id) is None

            response = client.get("/user/change_password/")
            assert response.status_code == 302
            assert "/user/login" in response.headers["Location"]
