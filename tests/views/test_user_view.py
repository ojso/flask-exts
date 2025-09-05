import pytest
from flask import url_for
from flask import session

from flask_exts.datastore.sqla import db
from flask_exts.views.user_view import UserView
from flask_exts.template.form.csrf import _get_csrf_token_of_session_and_g
from flask_exts.email.sender import Sender

mail_data = []


class EmailSender(Sender):
    def send(self, data):
        mail_data.append(data)


class TestUserView:
    def test_register(self, app, client, admin):
        # app.config.update(CSRF_ENABLED=False)
        with app.app_context():
            admin.add_view(UserView())
            db.create_all()

        email_sender = EmailSender()
        app.extensions["manager"].email.register_sender("verify_email", email_sender)

        with app.test_request_context():
            user_login_url = url_for("user.login")
            user_register_url = url_for("user.register")
            user_logout_url = url_for("user.logout")
            sess_csrf_token, csrf_token = _get_csrf_token_of_session_and_g()

        with client.session_transaction() as sess:
            sess["csrf_token"] = sess_csrf_token

        # register
        test_username = "test1234"
        test_password = "test1234"
        test_email = "test1234@test.com"
        rv = client.post(
            user_register_url,
            data={
                "username": test_username,
                "password": test_password,
                "password_repeat": test_password,
                "email": test_email,
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "inactive" in rv.text
        with client.session_transaction() as sess:
            assert "_user_id" in sess

        # logout
        client.get(user_logout_url)
        with client.session_transaction() as sess:
            assert "_user_id" not in sess

        # verify email
        verification_link = mail_data[0]["verification_link"]
        rv = client.get(verification_link, follow_redirects=True)
        assert rv.status_code == 200

        # relogin after email verified
        rv = client.post(
            user_login_url,
            data={
                "username": test_username,
                "password": test_password,
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        with client.session_transaction() as sess:
            assert "_user_id" in sess
        assert test_username in rv.text
        assert "inactive" not in rv.text

        # login with invalid name
        client.get(user_logout_url)
        test_invalid_name = "invalid_user_name"
        rv = client.post(
            user_login_url,
            data={
                "username": test_invalid_name,
                "password": test_password,
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "invalid username" in rv.text

    def test_tfa(self, app, client, admin):
        # app.config.update(CSRF_ENABLED=False)
        with app.app_context():
            admin.add_view(UserView())
            db.create_all()

        with app.test_request_context():
            user_login_url = url_for("user.login")
            user_register_url = url_for("user.register")
            user_logout_url = url_for("user.logout")
            user_enable_tfa_url = url_for("user.enable_tfa")
            user_setup_tfa_url = url_for("user.setup_tfa")
            sess_csrf_token, csrf_token = _get_csrf_token_of_session_and_g()

        with client.session_transaction() as sess:
            sess["csrf_token"] = sess_csrf_token

        # register
        test_username = "test1234"
        test_password = "test1234"
        test_email = "test1234@test.com"
        rv = client.post(
            user_register_url,
            data={
                "username": test_username,
                "password": test_password,
                "password_repeat": test_password,
                "email": test_email,
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200

        rv = client.get(user_enable_tfa_url, query_string={"enable": True})
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is True

        rv = client.get(user_enable_tfa_url, query_string={"enable": False})
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is False

        rv = client.get(user_setup_tfa_url)
        assert rv.status_code == 200
