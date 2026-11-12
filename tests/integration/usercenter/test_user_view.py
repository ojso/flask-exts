import re

import pytest
from flask import session, url_for

from flask_exts.datastore.sqla import db
from flask_exts.emailer.sender import Sender
from flask_exts.forms.form.csrf import get_csrf_token
from flask_exts.proxies import current_security, current_userstore
from flask_exts.security import (
    SESSION_KEY_PENDING_TFA_USER_ID,
    SESSION_KEY_TFA_RECOVERY,
    SESSION_KEY_TFA_VERIFIED,
)
from flask_exts.usercenter.forms.email_change import EmailChangeForm


@pytest.fixture
def mail_outbox():
    """Per-test mailbox for messages captured by EmailSender."""
    return []


class EmailSender(Sender):
    def __init__(self, outbox):
        self.outbox = outbox

    def send(self, data):
        self.outbox.append(data)


class TestUserView:
    @pytest.fixture
    def setup(self, app, client, mail_outbox):
        with app.app_context():
            db.create_all()

        email_sender = EmailSender(mail_outbox)
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
            self.user_rebind_tfa_url = url_for("user.rebind_tfa")
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
    def register_user(self, app, client, setup, mail_outbox):
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
            # is_active is an administrative lock, independent of email
            # verification -- a newly registered account is active by
            # default; it just hasn't verified its email yet.
            assert user.is_active is True
            assert user.email_verified is False

        verification_link = mail_outbox[-1]["verification_link"]
        client.get(verification_link, follow_redirects=True)

    @pytest.fixture
    def register_and_login_user(self, client, register_user):
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

    def test_register(self, client, setup, mail_outbox):
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

        # An account that hasn't verified its email yet is still active
        # (is_active is an administrative lock, not an email-verification
        # gate) -- it can sign in, see its profile, and use
        # account-authenticated features like change_password.
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
        assert "Email: Pending" in rv.text
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

        # The emailed verification link marks the email verified without
        # requiring another login, and without touching is_active.
        verification_link = mail_outbox[-1]["verification_link"]
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

    def test_register_rejects_invalid_email(self, app, client, setup):
        rv = client.post(
            self.user_register_url,
            data={
                "username": self.test_username,
                "password": self.test_password,
                "password_repeat": self.test_password,
                "email": "not-an-email",
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )

        assert rv.status_code == 200
        assert "Invalid email address." in rv.text
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

    def test_resend_email_verification(self, app, client, setup, mail_outbox):
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

        sent_before = len(mail_outbox)
        rv = client.post(
            self.user_resend_verification_url,
            data={"csrf_token": self.csrf_token},
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert rv.request.path.endswith("/profile/")
        assert "A new verification email has been sent." in rv.text
        assert len(mail_outbox) == sent_before + 1
        assert mail_outbox[-1]["email"] == self.test_email

        rv = client.get(mail_outbox[-1]["verification_link"])
        assert rv.status_code == 200
        with app.app_context():
            user = current_userstore.get_user_by_username(self.test_username)
            assert user.email_verified is True

    def test_change_email_requires_confirmation(
        self, app, client, register_and_login_user, mail_outbox
    ):
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
        assert mail_outbox[-1]["email"] == new_email

        with app.app_context():
            user = current_userstore.get_user_by_id(self.test_user_id)
            assert user.email == self.test_email
            assert user.email_verified is True

        rv = client.get(mail_outbox[-1]["verification_link"])
        assert rv.status_code == 200
        assert "Your email address has been verified." in rv.text
        with app.app_context():
            user = current_userstore.get_user_by_id(self.test_user_id)
            assert user.email == new_email
            assert user.email_verified is True

    def test_change_email_requires_correct_password(
        self, app, client, register_and_login_user, mail_outbox
    ):
        sent_before = len(mail_outbox)
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
        assert len(mail_outbox) == sent_before

    def test_change_email_rejects_invalid_address(
        self, client, register_and_login_user, mail_outbox
    ):
        sent_before = len(mail_outbox)
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
        assert len(mail_outbox) == sent_before

    def test_login_required_precedes_view_authorization(self, client, setup):
        response = client.get(self.user_setup_tfa_url)

        assert response.status_code == 302
        assert response.location.startswith(self.user_login_url)

    def test_tfa(self, app, client, register_and_login_user, monkeypatch):
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
            plaintext_totp_secret = u.get_totp_secret()
            encrypted_totp_secret = u.totp_secret
            tfa = current_security.get_plugin("two_factor_authentication")
            totp_code = tfa.get_totp_code(plaintext_totp_secret)

        assert f"<b>{plaintext_totp_secret}</b>" in rv.text
        assert f"<b>{encrypted_totp_secret}</b>" not in rv.text

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
            assert (
                SESSION_KEY_TFA_VERIFIED in sess
                and sess[SESSION_KEY_TFA_VERIFIED] is True
            )

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
            totp_code = tfa.get_totp_code(u.get_or_create_totp_secret())

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
            assert (
                SESSION_KEY_TFA_VERIFIED in sess
                and sess[SESSION_KEY_TFA_VERIFIED] is True
            )

        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            tfa = current_security.get_plugin("two_factor_authentication")
            totp_code = tfa.get_totp_code(u.get_or_create_totp_secret())

        # when tfa is enabled, tfa_verified is required to access setup_tfa
        rv = client.get(self.user_setup_tfa_url)
        assert rv.status_code == 200

        # logout
        client.get(self.user_logout_url)

        # relogin: password is correct, but TFA is enabled, so the login is
        # NOT established yet -- there must be no _user_id in the session,
        # only a pending-TFA marker.
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
            assert "_user_id" not in sess
            assert SESSION_KEY_PENDING_TFA_USER_ID in sess
            assert SESSION_KEY_TFA_VERIFIED not in sess

        # Nothing that requires login is reachable during the pending-TFA
        # window: a password-only login must not unlock anything.
        assert client.get(self.user_setup_tfa_url).status_code == 302
        assert client.get(self.user_change_password_url).status_code == 302
        assert client.get(self.user_index_url).status_code == 302

        # abandoning verify_tfa (e.g. closing the browser) and starting over
        # must require username/password again -- there is no persisted
        # half-login to resume.
        client.get(self.user_logout_url)
        with client.session_transaction() as sess:
            assert SESSION_KEY_PENDING_TFA_USER_ID not in sess
        assert (
            client.get(self.user_verify_tfa_url, follow_redirects=True).request.path
            == self.user_login_url
        )

        # restart the login
        rv = client.post(
            self.user_login_url,
            data={
                "username": self.test_username,
                "password": self.test_password,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.request.path == self.user_verify_tfa_url

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
            assert SESSION_KEY_PENDING_TFA_USER_ID not in sess
            assert (
                SESSION_KEY_TFA_VERIFIED in sess
                and sess[SESSION_KEY_TFA_VERIFIED] is True
            )

        # setup_tfa / change_password are reachable now that login is complete
        assert client.get(self.user_setup_tfa_url).status_code == 200
        assert client.get(self.user_change_password_url).status_code == 200

    def test_tfa_cannot_be_bypassed_after_password_login(
        self, app, client, register_and_login_user
    ):
        """Dedicated regression test: a correct password alone must never
        grant access to a TFA-enabled account. This is the exact bug class
        that was previously present (login_user was called before the TFA
        check), so it gets its own test independent of test_tfa.
        """
        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            tfa = current_security.get_plugin("two_factor_authentication")
            totp_code = tfa.get_totp_code(u.get_or_create_totp_secret())

        rv = client.post(
            self.user_enable_tfa_url,
            query_string={"enable": True},
            data={"csrf_token": self.csrf_token, "code": totp_code},
        )
        assert rv.json["tfa_enabled"] is True

        client.get(self.user_logout_url)
        with client.session_transaction() as sess:
            assert "_user_id" not in sess

        # Password-only login.
        rv = client.post(
            self.user_login_url,
            data={
                "username": self.test_username,
                "password": self.test_password,
                "csrf_token": self.csrf_token,
            },
        )
        assert rv.status_code == 302
        assert self.user_verify_tfa_url in rv.location

        # The password check alone must not establish a login session.
        with client.session_transaction() as sess:
            assert "_user_id" not in sess

        # Every login-gated endpoint must be unreachable in this window.
        for protected_url in (
            self.user_index_url,
            self.user_profile_url,
            self.user_setup_tfa_url,
            self.user_change_password_url,
            self.user_enable_tfa_url,
            self.user_recovery_codes_url,
        ):
            rv = client.get(protected_url)
            assert rv.status_code in (302, 403), (
                f"{protected_url} was reachable with password-only login "
                f"(status={rv.status_code})"
            )

    def test_disabling_account_invalidates_existing_session(
        self, app, client, register_and_login_user
    ):
        """Disabling an account takes effect on the next request: user_loader
        rejects inactive users and clears the session, so every login-required
        page redirects to the login page. Re-enabling the account does not
        resurrect the old cookie; a fresh login is required.
        """
        with app.app_context():
            current_userstore.user_set(
                current_userstore.get_user_by_id(self.test_user_id), is_active=False
            )

        for url in (
            self.user_index_url,
            self.user_profile_url,
            self.user_change_password_url,
            self.user_email_change_url,
            self.user_enable_tfa_url,
            self.user_setup_tfa_url,
            self.user_recovery_codes_url,
        ):
            rv = client.get(url)
            assert rv.status_code == 302, (
                f"{url} was reachable after the account was disabled "
                f"(status={rv.status_code})"
            )
            assert self.user_login_url in rv.location

        with client.session_transaction() as sess:
            assert "_user_id" not in sess

        # Re-enabling the account does not make the old cookie valid again.
        with app.app_context():
            current_userstore.user_set(
                current_userstore.get_user_by_id(self.test_user_id), is_active=True
            )
        assert client.get(self.user_index_url).status_code == 302

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

    def test_disabled_account_cannot_log_in(self, app, client, register_user):
        """is_active is an administrative lock: a disabled account must not
        get a session even when the password is correct, and must not be
        moved into the pending-TFA state either."""
        with app.app_context():
            current_userstore.user_set(
                current_userstore.get_user_by_id(self.test_user_id),
                tfa_enabled=True,
                is_active=False,
            )

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
        assert "This account has been disabled." in rv.text
        with client.session_transaction() as sess:
            assert "_user_id" not in sess
            assert SESSION_KEY_PENDING_TFA_USER_ID not in sess

    def test_disabled_account_cannot_complete_pending_tfa(
        self, app, client, register_user
    ):
        """A user disabled after the password step cannot finish TFA login."""
        with app.app_context():
            current_userstore.user_set(
                current_userstore.get_user_by_id(self.test_user_id),
                tfa_enabled=True,
                is_active=False,
            )

        with client.session_transaction() as sess:
            sess[SESSION_KEY_PENDING_TFA_USER_ID] = self.test_user_id

        rv = client.get(self.user_verify_tfa_url, follow_redirects=True)
        assert rv.status_code == 200
        assert rv.request.path == self.user_login_url
        with client.session_transaction() as sess:
            assert SESSION_KEY_PENDING_TFA_USER_ID not in sess
            assert "_user_id" not in sess

    def test_change_password(self, client, register_and_login_user):
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

    def test_forgot_password(self, client, register_and_login_user, mail_outbox):
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
        assert (
            "An email has been sent with instructions to reset your password."
            in rv.text
        )

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
        reset_password_mail_outbox = mail_outbox[-1]
        assert reset_password_mail_outbox["type"] == "reset_password"
        assert reset_password_mail_outbox["email"] == self.test_email
        assert "reset_password_link" in reset_password_mail_outbox
        reset_password_link = reset_password_mail_outbox["reset_password_link"]

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

    def test_recovery(self, app, client, register_user, mail_outbox):
        rv = client.get(self.user_recovery_codes_url)
        assert rv.status_code == 302

        # No pending TFA login exists yet (TFA isn't even enabled), so
        # recovery bounces to login rather than 403ing on an authenticated
        # user who isn't mid-TFA.
        rv = client.get(self.user_recovery_url, follow_redirects=True)
        assert rv.request.path == self.user_login_url

        # login
        rv = client.post(
            self.user_login_url,
            data={
                "username": self.test_username,
                "password": self.test_password,
                "csrf_token": self.csrf_token,
            },
            follow_redirects=True,
        )

        # tfa enable
        rv = client.get(self.user_setup_tfa_url)
        assert rv.status_code == 200

        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            tfa = current_security.get_plugin("two_factor_authentication")
            totp_code = tfa.get_totp_code(u.get_totp_secret())

        rv = client.post(
            self.user_enable_tfa_url,
            query_string={"enable": True},
            data={"csrf_token": self.csrf_token, "code": totp_code},
        )
        assert rv.status_code == 200
        assert rv.json["tfa_enabled"] is True
        with client.session_transaction() as sess:
            assert "_user_id" in sess
            assert (
                SESSION_KEY_TFA_VERIFIED in sess
                and sess[SESSION_KEY_TFA_VERIFIED] is True
            )

        # Capture the plaintext codes shown once; the database stores only hashes.
        rv = client.get(self.user_recovery_codes_url)
        assert rv.status_code == 200

        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            totp_secret = u.get_totp_secret()

        code_block = re.search(
            r'<pre id="recoveryCodes">\s*(.*?)\s*</pre>', rv.text, re.DOTALL
        )
        assert code_block is not None
        recovery_codes = re.findall(r"[A-Za-z0-9]{16}", code_block.group(1))
        assert len(recovery_codes) == 10
        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            assert all(code not in u.recovery_codes for code in recovery_codes)
            stored_recovery_codes = list(u.recovery_codes)

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

        # A recovery code completes the pending login and is removed from storage.
        recovery_code = recovery_codes[0]
        recovery_code_2 = recovery_codes[1]
        rv = client.post(
            self.user_recovery_url,
            data={"csrf_token": self.csrf_token, "code": recovery_code},
        )

        assert rv.status_code == 302
        assert rv.headers["Location"].endswith(self.user_index_url)
        with client.session_transaction() as sess:
            assert sess[SESSION_KEY_TFA_VERIFIED] is True

        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            recovery_codes_2 = u.recovery_codes
            assert u.get_totp_secret() == totp_secret
            consumed_code_hashes = [
                code
                for code in stored_recovery_codes
                if current_security.hasher.verify(recovery_code, code)
            ]

        assert len(recovery_codes_2) == len(stored_recovery_codes) - 1
        assert len(consumed_code_hashes) == 1
        assert recovery_codes_2 == [
            code for code in stored_recovery_codes if code not in consumed_code_hashes
        ]

        # Log in again and prove a different unused code still works.
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

        rv = client.post(
            self.user_recovery_url,
            data={"csrf_token": self.csrf_token, "code": recovery_code_2},
        )

        assert rv.status_code == 302
        assert rv.headers["Location"].endswith(self.user_index_url)
        with client.session_transaction() as sess:
            assert sess[SESSION_KEY_TFA_VERIFIED] is True

        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            recovery_codes_3 = u.recovery_codes
            assert u.get_totp_secret() == totp_secret
            # Match the plaintext code against hashes to identify what was consumed.
            consumed_code_hashes_2 = [
                code
                for code in recovery_codes_2
                if current_security.hasher.verify(recovery_code_2, code)
            ]

        assert len(recovery_codes_3) == len(recovery_codes_2) - 1
        assert len(consumed_code_hashes_2) == 1
        assert recovery_codes_3 == [
            code for code in recovery_codes_2 if code not in consumed_code_hashes_2
        ]

        # Recovery login grants a one-time path to bind a new authenticator.
        rv = client.get(self.user_setup_tfa_url)
        assert rv.status_code == 200
        assert "Rebind authenticator app" in rv.text

        rv = client.get(self.user_rebind_tfa_url)
        assert rv.status_code == 200
        assert "Verify and replace authenticator" in rv.text
        secret_match = re.search(r"<b>([A-Z2-7]+)</b>", rv.text)
        assert secret_match is not None
        new_totp_secret = secret_match.group(1)
        assert new_totp_secret != totp_secret

        with app.app_context():
            tfa = current_security.get_plugin("two_factor_authentication")
            new_totp_code = tfa.get_totp_code(new_totp_secret)

        invalid_totp_code = "000000" if new_totp_code != "000000" else "000001"
        rv = client.post(
            self.user_rebind_tfa_url,
            data={"csrf_token": self.csrf_token, "code": invalid_totp_code},
        )
        assert rv.status_code == 200
        assert "Invalid code" in rv.text
        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            assert u.get_totp_secret() == totp_secret
            assert u.recovery_codes == recovery_codes_3

        rv = client.post(
            self.user_rebind_tfa_url,
            data={"csrf_token": self.csrf_token, "code": new_totp_code},
        )
        assert rv.status_code == 200
        assert "Save these new recovery codes" not in rv.text

        with app.app_context():
            u = current_userstore.get_user_by_id(self.test_user_id)
            assert u.tfa_enabled is True
            assert u.get_totp_secret() == new_totp_secret
            rebound_hashes = list(u.recovery_codes)
            assert rebound_hashes == recovery_codes_3
            assert all(
                sum(
                    current_security.hasher.verify(code, stored_hash)
                    for stored_hash in rebound_hashes
                )
                == 1
                for code in recovery_codes[2:]
            )
            assert not any(
                current_security.hasher.verify(code, stored_hash)
                for code in recovery_codes[:2]
                for stored_hash in rebound_hashes
            )

        with client.session_transaction() as sess:
            assert SESSION_KEY_TFA_VERIFIED in sess
            assert SESSION_KEY_TFA_RECOVERY not in sess

        # Rebinding is available only during the recovery-authenticated session.
        assert client.get(self.user_rebind_tfa_url).status_code == 403
