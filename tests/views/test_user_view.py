import pytest
from flask import url_for
from flask import session
from flask_exts.datastore.sqla import db
from flask_exts.template.form.csrf import _get_csrf_token_of_session_and_g
from flask_exts.email.sender import Sender
from flask_exts.proxies import _security
from flask_exts.proxies import _userstore


mail_data = []


class EmailSender(Sender):
    def send(self, data):
        mail_data.append(data)


class TestUserView:
    @pytest.fixture
    def setup(self, app, client):
        # app.config.update(CSRF_ENABLED=False)
        with app.app_context():
            db.create_all()

        email_sender = EmailSender()
        app.extensions["exts"].email.register_sender("verify_email", email_sender)
        app.extensions["exts"].email.register_sender("reset_password", email_sender)
        # print(app.extensions["exts"].email.senders)

        with app.test_request_context():
            self.sess_csrf_token, self.csrf_token = _get_csrf_token_of_session_and_g()
            self.user_login_url = url_for("user.login")
            self.user_register_url = url_for("user.register")
            self.user_logout_url = url_for("user.logout")
            self.user_enable_tfa_url = url_for("user.enable_tfa")
            self.user_setup_tfa_url = url_for("user.setup_tfa")
            self.user_verify_tfa_url = url_for("user.verify_tfa")
            self.user_change_password_url = url_for("user.change_password")
            self.user_forgot_password_url = url_for("user.forgot_password")
            self.user_reset_password_url = url_for("user.reset_password")
            self.user_recovery_codes_url = url_for("user.recovery_codes")
            self.user_recovery_url = url_for("user.recovery")

        with client.session_transaction() as sess:
            sess["csrf_token"] = self.sess_csrf_token

        self.test_username = "test1234"
        self.test_password = "test1234"
        self.test_email = "test1234@test.com"

    @pytest.fixture
    def register_user(self, client, setup):
        rv = client.post(
            self.user_register_url,
            data={
                "username": self.test_username,
                "password": self.test_password,
                "password_repeat": self.test_password,
                "email": self.test_email,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            self.test_user_id = sess["_user_id"]

    @pytest.fixture
    def register_user_and_active(self, client, register_user):
        rv = client.post(
            self.user_register_url,
            data={
                "username": self.test_username,
                "password": self.test_password,
                "password_repeat": self.test_password,
                "email": self.test_email,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            self.test_user_id = sess["_user_id"]

        verification_link = mail_data[0]["verification_link"]
        rv = client.get(verification_link, follow_redirects=True)

    def test_register(self, client, setup):
        rv = client.post(
            self.user_register_url,
            data={
                "username": self.test_username,
                "password": self.test_password,
                "password_repeat": self.test_password,
                "email": self.test_email,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "inactive" in rv.text
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            test_user_id = sess["_user_id"]

        # print(mail_data)
        # logout
        client.get(self.user_logout_url)
        with client.session_transaction() as sess:
            assert "_user_id" not in sess

        # login with invalid username
        rv = client.post(
            self.user_login_url,
            data={
                "username": "invalid_username",
                "password": self.test_password,
                "csrf_token": self.csrf_token,
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
            self.user_login_url,
            data={
                "username": self.test_username,
                "password": self.test_password,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        with client.session_transaction() as sess:
            assert "_user_id" in sess
        assert self.test_username in rv.text
        assert "inactive" not in rv.text

    def test_tfa(self, app, client, register_user):
        # get tfa_enabled status
        rv = client.get(self.user_enable_tfa_url)
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is False

        # get verify_tfa modal page
        rv = client.get(
            self.user_verify_tfa_url,
            query_string={"modal": True, "action": self.user_enable_tfa_url},
        )
        assert rv.status_code == 200
        # print(rv.text)
        assert "form" in rv.text
        assert self.user_enable_tfa_url in rv.text

        # when tfa is not enabled, setup_tfa
        rv = client.get(self.user_setup_tfa_url)
        assert rv.status_code == 200
        # for key, value in rv.headers.items():
        # print(f"{key}: {value}")
        assert (
            rv.headers.get("Cache-Control")
            == "no-cache, no-store, must-revalidate, max-age=0"
        )
        assert rv.headers.get("Pragma") == "no-cache"
        assert rv.headers.get("Expires") == "0"

        with app.app_context():
            u = _userstore.get_user_by_id(self.test_user_id)
            totp_code = _security.tfa.get_totp_code(u.totp_secret)

        # enable tfa without code
        rv = client.get(self.user_enable_tfa_url, query_string={"enable": True})
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is False

        # enable tfa with code
        rv = client.post(
            self.user_enable_tfa_url,
            query_string={"enable": True},
            data={"csrf_token": self.csrf_token, "code": totp_code},
        )
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is True
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert "tfa_verified" in sess and sess["tfa_verified"] is True

        # disable tfa
        rv = client.post(
            self.user_enable_tfa_url,
            query_string={"enable": False},
            data={"csrf_token": self.csrf_token, "code": totp_code},
        )
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is False
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert "tfa_verified" not in sess

        with app.app_context():
            u = _userstore.get_user_by_id(self.test_user_id)
            totp_code = _security.tfa.get_totp_code(u.totp_secret)

        assert u.totp_secret is None

        # refresh setup_tfa page to generate new totp_secret
        rv = client.get(self.user_setup_tfa_url)
        with app.app_context():
            u = _userstore.get_user_by_id(self.test_user_id)
            totp_code = _security.tfa.get_totp_code(u.totp_secret)

        assert u.totp_secret is not None

        # enable tfa again
        rv = client.post(
            self.user_enable_tfa_url,
            query_string={"enable": True},
            data={"csrf_token": self.csrf_token, "code": totp_code},
        )
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is True
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert "tfa_verified" in sess and sess["tfa_verified"] is True

        with app.app_context():
            u = _userstore.get_user_by_id(self.test_user_id)
            totp_code = _security.tfa.get_totp_code(u.totp_secret)

        # when tfa is enabled, tfa_verified is required to access setup_tfa
        rv = client.get(self.user_setup_tfa_url)
        assert rv.status_code == 200

        # logout
        client.get(self.user_logout_url)

        # relogin
        rv = client.post(
            self.user_login_url,
            data={
                "username": self.test_username,
                "password": self.test_password,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert rv.request.path == self.user_verify_tfa_url

        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert "tfa_verified" not in sess

        # verify tfa
        rv = client.get(self.user_verify_tfa_url)
        assert rv.status_code == 200

        rv = client.post(
            self.user_verify_tfa_url,
            data={
                "code": totp_code,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert "tfa_verified" in sess and sess["tfa_verified"] is True

    def test_change_password(self, client, register_user):
        rv = client.get(self.user_change_password_url)
        assert rv.status_code == 200

        # change password with invalid old_password
        new_password = "newpassword1234"
        rv = client.post(
            self.user_change_password_url,
            data={
                "old_password": "invalidpassword",
                "new_password": new_password,
                "new_password_repeat": new_password,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "Invalid password" in rv.text

        # change password with non-matching repeat
        new_password = "newpassword1234"
        rv = client.post(
            self.user_change_password_url,
            data={
                "old_password": self.test_password,
                "new_password": new_password,
                "new_password_repeat": "invalidrepeat",
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "Field must be equal to new_password" in rv.text

        # change password successfully
        new_password = "newpassword1234"
        rv = client.post(
            self.user_change_password_url,
            data={
                "old_password": self.test_password,
                "new_password": new_password,
                "new_password_repeat": new_password,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200

        # logout
        client.get(self.user_logout_url)
        with client.session_transaction() as sess:
            assert "_user_id" not in sess

        # login with old password
        rv = client.post(
            self.user_login_url,
            data={
                "username": self.test_username,
                "password": self.test_password,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "invalid password" in rv.text

        # login with new password
        rv = client.post(
            self.user_login_url,
            data={
                "username": self.test_username,
                "password": new_password,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        with client.session_transaction() as sess:
            assert "_user_id" in sess
        assert self.test_username in rv.text

    def test_forgot_password(self, client, register_user_and_active):
        # logout
        client.get(self.user_logout_url)

        # access forgot_password page
        rv = client.get(self.user_forgot_password_url)
        assert rv.status_code == 200
        assert "form" in rv.text

        # submit invalid email
        rv = client.post(
            self.user_forgot_password_url,
            data={
                "email": "invalid@example.com",
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "Found no user with this email" in rv.text

        # forgot password successfully
        rv = client.post(
            self.user_forgot_password_url,
            data={
                "email": self.test_email,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        reset_password_mail_data = mail_data[-1]
        assert reset_password_mail_data["type"] == "reset_password"
        assert reset_password_mail_data["email"] == self.test_email
        assert "reset_password_link" in reset_password_mail_data
        reset_password_link = reset_password_mail_data["reset_password_link"]

        # reset password with new password
        newpassword = "newpassword1234"
        rv = client.post(
            reset_password_link,
            data={
                "password": newpassword,
                "password_repeat": newpassword,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200

        # login with new password
        rv = client.post(
            self.user_login_url,
            data={
                "username": self.test_username,
                "password": newpassword,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        with client.session_transaction() as sess:
            assert "_user_id" in sess
        assert self.test_username in rv.text

    def test_recovery(self, app, client, register_user):
        rv = client.get(self.user_recovery_codes_url)
        assert rv.status_code == 403

        rv = client.get(self.user_recovery_url)
        assert rv.status_code == 403

        # tfa enable
        rv = client.get(self.user_setup_tfa_url)
        assert rv.status_code == 200

        with app.app_context():
            u = _userstore.get_user_by_id(self.test_user_id)
            totp_code = _security.tfa.get_totp_code(u.totp_secret)

        rv = client.post(
            self.user_enable_tfa_url,
            query_string={"enable": True},
            data={"csrf_token": self.csrf_token, "code": totp_code},
        )
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is True
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert "tfa_verified" in sess and sess["tfa_verified"] is True

        # show recovery codes
        rv = client.get(self.user_recovery_codes_url)
        assert rv.status_code == 200

        with app.app_context():
            u = _userstore.get_user_by_id(self.test_user_id)
            totp_secret = u.totp_secret
            recovery_codes = u.recovery_codes

        assert recovery_codes[0] in rv.text

        rv = client.get(self.user_recovery_url)
        assert rv.status_code == 200

        # recovery to get totp_secret
        recovery_code = recovery_codes[0]
        rv = client.post(
            self.user_recovery_url,
            data={"csrf_token": self.csrf_token, "code": recovery_code},
        )

        assert rv.status_code == 200
        assert totp_secret in rv.text

        # u.recovery_codes removed recovery_code
        with app.app_context():
            u = _userstore.get_user_by_id(self.test_user_id)
            recovery_codes_2 = u.recovery_codes

        assert len(recovery_codes) == len(recovery_codes_2) + 1
        assert recovery_code not in recovery_codes_2
