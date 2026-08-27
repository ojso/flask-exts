from flask_exts.proxies import current_security
from flask_exts.proxies import current_userstore
from flask_exts.datastore.sqla import db


class TestSecurity:
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
            status, user = current_userstore.create_user(
                username="testuser",
                password="testpassword",
                email="testuser@example.com",
            )
            assert status == "ok"
            assert user is not None
            assert user.is_active is False
            ev = current_security.get_plugin("email_verification")
            token = ev.generate_token(user)
            r = ev.execute_with_token(token)
            assert r[0] == "verified"
            assert r[1].email_verified is True
            assert r[1].is_active is True
