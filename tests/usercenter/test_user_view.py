import re

import pytest
from flask import session, url_for

from flask_exts.datastore.sqla import db
from flask_exts.emailer.sender import Sender
from flask_exts.forms.form.csrf import get_csrf_token
from flask_exts.proxies import current_security, current_userstore
from flask_exts.security import SESSION_KEY_TFA_VERIFIED
from flask_exts.usercenter.forms.email_change import EmailChangeForm

mail_data = []


class EmailSender(Sender):
    def send(self, data):
        mail_data.append(data)


class TestUserView:
    @pytest.fixture
    def setup(self, app, client):
        with app.app_context():
            db.create_all()

        email_sender = EmailSender()
        email = app.extensions["exts"].get_extension("emailer").get_emailer()
        email.register_sender("verify_email", email_sender)
        email.register_sender("reset_password", email_sender)
        # print(email.senders)

        with app.test_request_context():
            self.user_login_url = url_for("user.login")
            self.user_register_url = url_for("user.register")
            self.user_index_url = url_for("user.index")
            self.user_profile_url = url_for("user.profile")
            self.user_email_change_url = url_for("user.email_change")
            self.user_resend_verification_url = url_for("user.resend_verification")
            self.user_logout_url = url_for("user.logout")
            self.user_enable_tfa_url = url_for("user.enable_tfa")
            self.user_setup_tfa_url = url_for("user.setup_tfa")
            self.user_verify_tfa_url = url_for("user.verify_tfa")
            self.user_change_password_url = url_for("user.change_password")
            self.user_forgot_password_url = url_for("user.forgot_password")
            self.user_reset_password_url = url_for("user.reset_password")
            self.user_recovery_codes_url = url_for("user.recovery_codes")
            self.user_recovery_url = url_for("user.recovery")

        # generate csrf_token for the current request and set it to session and g,
        # then pass it to the test client session for later use in form submission.
        with app.test_request_context():
            self.csrf_token = get_csrf_token()
            session_csrf_token = session.get("csrf_token")
        with client.session_transaction() as sess:
            sess["csrf_token"] = session_csrf_token

        self.test_username = "test1234"
        self.test_password = "test1234"
        self.test_email = "test1234@test.com"

    @pytest.fixture
    def register_user(self, app, client, setup):
        client.post(
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
        with app.app_context():
            user = current_userstore.get_user_by_username(self.test_username)
            self.test_user_id = user.id
            assert user.is_active is False

        verification_link = mail_data[-1]["verification_link"]
        client.get(verification_link, follow_redirects=True)
        client.post(
            self.user_login_url,
            data={
                "username": self.test_username,
                "password": self.test_password,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        with client.session_transaction() as sess:
            assert "_user_id" in sess

    @pytest.fixture
    def register_user_and_active(self, register_user):
        return register_user

    def test_register(self, client, setup):
        with client.application.app_context():
            current_security.get_plugin("authorizer").admin_allow_access = False

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
        assert "verify your account" in rv.text
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
        assert "Invalid username or password." in rv.text

        # An unverified account can sign in to its profile, but cannot use
        # authenticated features until email verification completes.
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
        assert self.test_username in rv.text
        assert "verify your email" in rv.text.lower()
        with client.session_transaction() as sess:
            assert "_user_id" in sess

        rv = client.get(self.user_change_password_url)
        assert rv.status_code == 200

        rv = client.get(self.user_logout_url, follow_redirects=True)
        assert rv.status_code == 200
        with client.session_transaction() as sess:
            assert "_user_id" not in sess

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

        # The emailed verification link activates the account without
        # requiring another login.
        verification_link = mail_data[-1]["verification_link"]
        rv = client.get(verification_link, follow_redirects=True)
        assert rv.status_code == 200
        assert self.test_username in rv.text
        with client.session_transaction() as sess:
            assert "_user_id" in sess

        rv = client.get(self.user_change_password_url)
        assert rv.status_code == 200

    def test_register_rejects_duplicate_email(self, app, client, setup):
        with app.app_context():
            current_userstore.create_user(
                username="existing_user",
                password=self.test_password,
                email=self.test_email,
            )

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
        assert "Email already exists." in rv.text
        with app.app_context():
            assert current_userstore.get_user_by_username(self.test_username) is None

    def test_email_change_form_rejects_duplicate_email(self, app, setup):
        with app.app_context():
            current_userstore.create_user(
                username="existing_user",
                password=self.test_password,
                email=self.test_email,
            )

        with app.test_request_context():
            form = EmailChangeForm(
                data={
                    "email": self.test_email,
                    "current_password": self.test_password,
                }
            )
            assert not form.validate()
            assert form.email.errors == ["Email already exists."]

    def test_resend_email_verification(self, app, client, setup):
        with app.app_context():
            current_userstore.create_user(
                username=self.test_username,
                password=self.test_password,
                email=self.test_email,
            )

        rv = client.post(
            self.user_login_url,
            data={
                "username": self.test_username,
                "password": self.test_password,
                "csrf_token": self.csrf_token,
            },
        )
        assert rv.status_code == 302

        rv = client.get(self.user_index_url)
        assert "View Profile" in rv.text
        assert "Log Out" in rv.text

        rv = client.get(self.user_profile_url)
        assert "Resend Verification Email" in rv.text
        assert "Change Email" in rv.text
        assert "Change Password" in rv.text
        assert "Two-Factor" in rv.text

        sent_before = len(mail_data)
        rv = client.post(
            self.user_resend_verification_url,
            data={"csrf_token": self.csrf_token},
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert rv.request.path.endswith("/profile/")
        assert "A new verification email has been sent." in rv.text
        assert len(mail_data) == sent_before + 1
        assert mail_data[-1]["email"] == self.test_email

        rv = client.get(mail_data[-1]["verification_link"])
        assert rv.status_code == 200
        with app.app_context():
            user = current_userstore.get_user_by_username(self.test_username)
            assert user.email_verified is True

    def test_change_email_requires_confirmation(self, app, client, register_user):
        new_email = "updated@example.com"
        rv = client.get(self.user_profile_url)
        assert rv.status_code == 200
        assert "Profile" in rv.text
        assert self.test_email in rv.text
        assert self.user_email_change_url in rv.text

        rv = client.post(
            self.user_email_change_url,
            data={
                "email": new_email,
                "current_password": self.test_password,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "confirmation link has been sent" in rv.text.lower()
        assert mail_data[-1]["email"] == new_email

        with app.app_context():
            user = current_userstore.get_user_by_id(self.test_user_id)
            assert user.email == self.test_email
            assert user.email_verified is True

        rv = client.get(mail_data[-1]["verification_link"])
        assert rv.status_code == 200
        assert "Your email address has been verified." in rv.text
        with app.app_context():
            user = current_userstore.get_user_by_id(self.test_user_id)
            assert user.email == new_email
            assert user.email_verified is True

    def test_change_email_requires_correct_password(self, app, client, register_user):
        sent_before = len(mail_data)
        rv = client.post(
            self.user_email_change_url,
            data={
                "email": "updated@example.com",
                "current_password": "incorrect password",
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "Invalid password." in rv.text
        assert len(mail_data) == sent_before

    def test_change_email_rejects_invalid_address(self, client, register_user):
        sent_before = len(mail_data)
        rv = client.post(
            self.user_email_change_url,
            data={
                "email": "not-an-email",
                "current_password": self.test_password,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "Invalid email address." in rv.text
        assert len(mail_data) == sent_before

    def test_tfa(self, app, client, register_user, monkeypatch):
        # get tfa_enabled status
        rv = client.get(self.user_enable_tfa_url)
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is False

        # when tfa is not enabled, setup_tfa
        rv = client.get(self.user_setup_tfa_url)
        assert rv.status_code == 200
        assert "data-modal-form" in rv.text
        assert "data-fields=" in rv.text
        assert "&#34;code&#34;" in rv.text
        assert "fa_modal_window" not in rv.text
        assert "enable_tfa" in rv.text
        assert 'data-csrf-required="false"' in rv.text
        assert 'type="module"' in rv.text
        assert "import ModalForm" in rv.text
        # for key, value in rv.headers.items():
        # print(f"{key}: {value}")
        assert (
            rv.headers.get("Cache-Control")
            == "no-cache, no-store, must-revalidate, max-age=0"
        )
        assert rv.headers.get("Pragma") == "no-cache"
        assert rv.headers.get("Expires") == "0"

        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            tfa = current_security.get_plugin("two_factor_authentication")
            totp_code = tfa.get_totp_code(u.totp_secret)

        # enable tfa without code
        rv = client.get(self.user_enable_tfa_url, query_string={"enable": True})
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is False

        # With CSRF disabled, JSON submission needs no CSRF token. Invalid
        # codes return the field-error shape expected by ModalForm.
        rv = client.post(
            self.user_enable_tfa_url,
            query_string={"enable": True},
            json={"code": "ABCDEF"},
        )
        assert rv.status_code == 422
        assert rv.json["errors"]["code"] == "Invalid code"
        assert "ok" not in rv.json

        monkeypatch.setitem(app.config, "CSRF_ENABLED", True)
        rv = client.post(
            self.user_enable_tfa_url,
            query_string={"enable": True},
            json={"code": totp_code},
        )
        assert rv.status_code == 400

        # enable tfa with a valid code
        rv = client.post(
            self.user_enable_tfa_url,
            query_string={"enable": True},
            json={"csrf_token": self.csrf_token, "code": totp_code},
        )
        assert rv.status_code == 200
        with client.session_transaction() as sess:
            assert "_user_id" in sess
        assert rv.json["tfa_enabled"] is True
        assert "ok" not in rv.json
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert SESSION_KEY_TFA_VERIFIED in sess and sess[SESSION_KEY_TFA_VERIFIED] is True

        rv = client.get(self.user_setup_tfa_url)
        assert rv.status_code == 200
        assert "Disable 2FA" in rv.text
        assert "data-modal-form" in rv.text

        # disable tfa
        with client.session_transaction() as sess:
            sess.pop(SESSION_KEY_TFA_VERIFIED, None)
        rv = client.post(
            self.user_enable_tfa_url,
            query_string={"enable": False},
            json={"csrf_token": self.csrf_token, "code": totp_code},
        )
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is False
        assert "ok" not in rv.json
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert SESSION_KEY_TFA_VERIFIED not in sess
        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            tfa = current_security.get_plugin("two_factor_authentication")
            totp_code = tfa.get_totp_code(u.totp_secret)

        assert u.totp_secret is None

        # refresh setup_tfa page to generate new totp_secret
        rv = client.get(self.user_setup_tfa_url)
        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            tfa = current_security.get_plugin("two_factor_authentication")
            totp_code = tfa.get_totp_code(u.totp_secret)

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
            assert SESSION_KEY_TFA_VERIFIED in sess and sess[SESSION_KEY_TFA_VERIFIED] is True

        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            tfa = current_security.get_plugin("two_factor_authentication")
            totp_code = tfa.get_totp_code(u.totp_secret)

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
            assert SESSION_KEY_TFA_VERIFIED not in sess

        assert client.get(self.user_setup_tfa_url).status_code == 200
        assert client.get(self.user_change_password_url).status_code == 200

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
            assert SESSION_KEY_TFA_VERIFIED in sess and sess[SESSION_KEY_TFA_VERIFIED] is True

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
        assert "Invalid username or password." in rv.text

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
        invalid_email_response = rv.text
        assert "An email has been sent with instructions to reset your password." in rv.text

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
        assert rv.text == invalid_email_response
        reset_password_mail_data = mail_data[-1]
        assert reset_password_mail_data["type"] == "reset_password"
        assert reset_password_mail_data["email"] == self.test_email
        assert "reset_password_link" in reset_password_mail_data
        reset_password_link = reset_password_mail_data["reset_password_link"]

        rv = client.post(
            self.user_reset_password_url,
            query_string={"token": "invalid-token"},
            data={
                "password": "newpassword1234",
                "password_repeat": "newpassword1234",
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "invalid or has expired" in rv.text

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
            u = current_userstore.get_user_by_id(self.test_user_id)
            tfa = current_security.get_plugin("two_factor_authentication")
            totp_code = tfa.get_totp_code(u.totp_secret)

        rv = client.post(
            self.user_enable_tfa_url,
            query_string={"enable": True},
            data={"csrf_token": self.csrf_token, "code": totp_code},
        )
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is True
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert SESSION_KEY_TFA_VERIFIED in sess and sess[SESSION_KEY_TFA_VERIFIED] is True

        # show recovery codes
        rv = client.get(self.user_recovery_codes_url)
        assert rv.status_code == 200

        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            totp_secret = u.totp_secret

        code_block = re.search(
            r'<pre id="recoveryCodes">\s*(.*?)\s*</pre>', rv.text, re.DOTALL
        )
        assert code_block is not None
        recovery_codes = re.findall(r"[A-Za-z0-9]{16}", code_block.group(1))
        assert len(recovery_codes) == 10
        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            assert all(code not in u.recovery_codes for code in recovery_codes)

        client.get(self.user_logout_url)
        client.post(
            self.user_login_url,
            data={
                "username": self.test_username,
                "password": self.test_password,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        rv = client.get(self.user_recovery_url)
        assert rv.status_code == 200

        # recovery to get totp_secret
        recovery_code = recovery_codes[0]
        rv = client.post(
            self.user_recovery_url,
            data={"csrf_token": self.csrf_token, "code": recovery_code},
        )

        assert rv.status_code == 200
        assert "Save these new recovery codes" in rv.text
        with client.session_transaction() as sess:
            assert sess[SESSION_KEY_TFA_VERIFIED] is True

        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            recovery_codes_2 = u.recovery_codes
            new_totp_secret = u.totp_secret

        assert new_totp_secret != totp_secret
        assert recovery_code not in recovery_codes_2
        assert all(code not in recovery_codes_2 for code in recovery_codes)
