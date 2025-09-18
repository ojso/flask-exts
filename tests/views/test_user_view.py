import pytest
from flask import url_for
from flask import session
from flask_exts.datastore.sqla import db
from flask_exts.views.user_view import UserView
from flask_exts.template.form.csrf import _get_csrf_token_of_session_and_g
from flask_exts.email.sender import Sender
from flask_exts.proxies import _security
from flask_exts.proxies import _userstore


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
            sess_csrf_token, csrf_token = _get_csrf_token_of_session_and_g()
            user_login_url = url_for("user.login")
            user_register_url = url_for("user.register")
            user_logout_url = url_for("user.logout")
            user_enable_tfa_url = url_for("user.enable_tfa")
            user_setup_tfa_url = url_for("user.setup_tfa")
            user_verify_tfa_url = url_for("user.verify_tfa")
            user_verify_tfa_modal_url = url_for("user.verify_tfa_modal")

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
            test_user_id = sess["_user_id"]

        # logout
        client.get(user_logout_url)
        with client.session_transaction() as sess:
            assert "_user_id" not in sess

        # login with invalid username
        rv = client.post(
            user_login_url,
            data={
                "username": "invalid_username",
                "password": test_password,
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "invalid username" in rv.text

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

        # get tfa_enabled status
        rv = client.get(user_enable_tfa_url)
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is False

        # get verify_tfa modal page
        rv = client.get(
            user_verify_tfa_modal_url,
            query_string={"modal": True, "action": user_enable_tfa_url},
        )
        assert rv.status_code == 200
        # print(rv.text)
        assert "form" in rv.text
        assert user_enable_tfa_url in rv.text

        # when tfa is not enabled, setup_tfa
        rv = client.get(user_setup_tfa_url)
        assert rv.status_code == 200
        # for key, value in rv.headers.items():
        # print(f"{key}: {value}")
        assert (
            rv.headers.get("Cache-Control")
            == "no-cache, no-store, must-revalidate, max-age=0"
        )
        assert rv.headers.get("Pragma") == "no-cache"
        assert rv.headers.get("Expires") == "0"

        # enable tfa without code
        rv = client.get(user_enable_tfa_url, query_string={"enable": True})
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is False

        with app.app_context():
            u = _userstore.get_user_by_id(test_user_id)
            totp_code = _security.tfa.get_totp_code(u.totp_secret)

        # enable tfa with code
        rv = client.post(
            user_enable_tfa_url,
            query_string={"enable": True},
            data={"csrf_token": csrf_token, "code": totp_code},
        )
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is True
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert "tfa_verified" in sess and sess["tfa_verified"] is True

        # disable tfa
        rv = client.post(
            user_enable_tfa_url,
            query_string={"enable": False},
            data={"csrf_token": csrf_token, "code": totp_code},
        )
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is False
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert "tfa_verified" not in sess

        # enable tfa again
        rv = client.post(
            user_enable_tfa_url,
            query_string={"enable": True},
            data={"csrf_token": csrf_token, "code": totp_code},
        )
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is True
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert "tfa_verified" in sess and sess["tfa_verified"] is True

        # when tfa is enabled, tfa_verified is required to access setup_tfa
        rv = client.get(user_setup_tfa_url)
        assert rv.status_code == 403

        # logout
        client.get(user_logout_url)

        # relogin
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
        assert rv.request.path == user_verify_tfa_url
        
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert "tfa_verified" not in sess

        # verify tfa
        rv = client.get(user_verify_tfa_url)
        assert rv.status_code == 200

        rv = client.post(
            user_verify_tfa_url,
            data={
                "code": totp_code,
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert "tfa_verified" in sess and sess["tfa_verified"] is True


