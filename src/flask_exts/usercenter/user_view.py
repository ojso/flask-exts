from hmac import compare_digest

from flask import (
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.datastructures import MultiDict

from ..admin import View, expose_url
from ..constants import NO_CACHE_HEADER
from ..proxies import current_security, current_userstore
from ..security import SESSION_KEY_TFA_VERIFIED
from ..security.exceptions import TokenActionError
from ..security.urls import safe_redirect_target
from ..signals import user_registered
from ..userstore.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from .forms.change_password import ChangePasswordForm
from .forms.email_change import EmailChangeForm
from .forms.forgot_password import ForgotPasswordForm
from .forms.login import LoginForm
from .forms.recovery import RecoveryForm
from .forms.register import RegisterForm
from .forms.resend_verification import ResendVerificationForm
from .forms.reset_password import ResetPasswordForm
from .forms.two_factor import TwoFactorForm


class UserView(View):
    """
    Default administrative interface index page when visiting the ``/user/`` URL.
    """

    allow_access = True

    index_template = "user/index.html"
    list_template = "user/list.html"
    login_template = "user/login.html"
    register_template = "user/register.html"
    verify_email_template = "user/verify_email.html"

    def __init__(
        self,
        name="User",
        endpoint="user",
        url="/user",
        template_folder=None,
        static_folder=None,
        static_url_path=None,
    ):
        super().__init__(
            name=name,
            endpoint=endpoint,
            url=url,
            template_folder=template_folder,
            static_folder=static_folder,
            static_url_path=static_url_path,
        )

    def get_login_form_class(self):
        return LoginForm

    def register_form(self, *args, **kwargs):
        return RegisterForm(*args, **kwargs)

    @login_required
    @expose_url("/index/")
    def index(self):
        return self.render(
            self.index_template, resend_form=ResendVerificationForm()
        )

    @login_required
    @expose_url("/profile/")
    def profile(self):
        return self.render(
            "user/profile.html", resend_form=ResendVerificationForm()
        )

    @login_required
    @expose_url("/email_change/", methods=("GET", "POST"))
    def email_change(self):
        form = EmailChangeForm()
        if form.validate_on_submit():
            if form.email.data == current_user.email:
                flash("This is already your current email address.", "error")
            else:
                current_security.get_plugin("email_change").send_token(
                    current_user, form.email.data
                )
                flash(
                    "A confirmation link has been sent to your new email address. "
                    "Your current email remains active until you confirm it.",
                    "success",
                )
                return redirect(url_for(".profile"))
        return self.render("user/email_change.html", form=form)

    @login_required
    @expose_url("/resend_verification/", methods=("POST",))
    def resend_verification(self):
        form = ResendVerificationForm()
        if not form.validate_on_submit():
            abort(400)
        if current_user.email_verified:
            flash("Your email address is already verified.", "info")
        elif current_user.email:
            current_security.get_plugin("email_verification").send_token(
                current_user
            )
            flash("A new verification email has been sent.", "success")
        else:
            flash("No email address is associated with this account.", "error")
        return redirect(url_for(".profile"))

    @expose_url("/login/", methods=("GET", "POST"))
    def login(self):
        if current_user.is_authenticated:
            return redirect(url_for(".index"))
        form = self.get_login_form_class()()
        if form.validate_on_submit():
            try:
                user = current_userstore.login_user_by_username_password(
                    form.username.data, form.password.data
                )
            except InvalidCredentialsError as error:
                form[error.field].errors.append(str(error))
            else:
                login_kwargs = {}
                if hasattr(form, "remember_me"):
                    login_kwargs["remember"] = form.remember_me.data
                # force=True to bypass the is_active check, since we handle it in the allow method
                if not login_user(user, force=True, **login_kwargs):
                    form.username.errors.append("Invalid username or password.")
                else:
                    next_page = safe_redirect_target(
                        request.args.get("next"), url_for(".index")
                    )
                    if user.tfa_enabled:
                        return redirect(url_for(".verify_tfa", next=next_page))
                    return redirect(next_page)
        return self.render(self.login_template, form=form)

    @expose_url("/register/", methods=("GET", "POST"))
    def register(self):
        if current_user.is_authenticated:
            return redirect(url_for(".index"))
        form = self.register_form()
        if form.validate_on_submit():
            try:
                user = current_userstore.create_user(
                    username=form.username.data,
                    password=form.password.data,
                    email=form.email.data,
                )
            except UserAlreadyExistsError as error:
                flash(str(error), "error")
            else:
                user_registered.send(current_app._get_current_object(), user=user)
                flash(
                    "Account created. Please check your email to verify your account.",
                    "success",
                )
                return redirect(url_for(".login"))

        return self.render(self.register_template, form=form)

    @expose_url("/logout/")
    def logout(self):
        logout_user()
        if SESSION_KEY_TFA_VERIFIED in session:
            session.pop(SESSION_KEY_TFA_VERIFIED)
        return redirect(url_for(".login"))

    @expose_url("/verify_email/")
    def verify_email(self):
        token = request.args.get("token")
        try:
            result = current_security.get_plugin(
                "email_verification"
            ).execute_with_token(
                token
            )
        except TokenActionError as error:
            result = error.status
        return self.render(self.verify_email_template, result=result)

    @expose_url("/confirm_email_change/")
    def confirm_email_change(self):
        token = request.args.get("token")
        try:
            result = current_security.get_plugin("email_change").execute_with_token(
                token
            )
        except TokenActionError as error:
            result = error.status
        except UserAlreadyExistsError:
            result = "email_exists"
        return self.render(self.verify_email_template, result=result)

    @login_required
    @expose_url("/enable_tfa/", methods=("GET", "POST"))
    def enable_tfa(self):
        enable = request.args.get("enable")
        if enable is None:
            return jsonify({"tfa_enabled": current_user.tfa_enabled})
        if request.method == "GET":
            return jsonify({"tfa_enabled": current_user.tfa_enabled})

        enable = not str(enable).lower() in ["0", "false"]
        if current_user.tfa_enabled == enable:
            return jsonify({"tfa_enabled": current_user.tfa_enabled})

        if request.is_json:
            data = request.get_json(silent=True)
            if not isinstance(data, dict):
                return jsonify({"message": "Invalid form submission"}), 400
            form = TwoFactorForm(formdata=MultiDict(data))
        else:
            form = TwoFactorForm()

        if not form.validate_on_submit():
            csrf_field = current_app.config.get("CSRF_FIELD_NAME", "csrf_token")
            errors = {
                name: messages[0]
                for name, messages in form.errors.items()
                if name != csrf_field and messages
            }
            if errors:
                return jsonify(
                    {
                        "message": "Invalid form submission",
                        "errors": errors,
                    }
                ), 422
            return jsonify({"message": "Invalid form submission"}), 400

        tfa = current_security.get_plugin("two_factor_authentication")
        if not tfa.verify_totp(current_user.totp_secret, form.code.data):
            return jsonify(
                {
                    "message": "Invalid code",
                    "errors": {"code": "Invalid code"},
                }
            ), 422

        current_userstore.user_set(current_user, tfa_enabled=enable)
        if enable:
            session[SESSION_KEY_TFA_VERIFIED] = True
        else:
            session.pop(SESSION_KEY_TFA_VERIFIED, None)
            current_userstore.user_set(current_user, totp_secret=None)

        return jsonify({"tfa_enabled": current_user.tfa_enabled})

    @login_required
    @expose_url("/setup_tfa/")
    def setup_tfa(self):
        if current_user.tfa_enabled:
            return self.render(
                "user/show_tfa.html",
            )
        tfa = current_security.get_plugin("two_factor_authentication")
        if not current_user.totp_secret:
            current_userstore.user_set(
                current_user, totp_secret=tfa.generate_totp_secret()
            )

        totp_uri = tfa.get_totp_uri(current_user.totp_secret, current_user.username)
        return self.render(
            "user/setup_tfa.html",
            totp_uri=totp_uri,
            totp_secret=current_user.totp_secret,
            _headers=NO_CACHE_HEADER,
        )

    @login_required
    @expose_url("/verify_tfa/", methods=("GET", "POST"))
    def verify_tfa(self):
        if not current_user.tfa_enabled:
            abort(403)
        if session.get(SESSION_KEY_TFA_VERIFIED):
            abort(403)

        form = TwoFactorForm()
        if form.validate_on_submit():
            tfa = current_security.get_plugin("two_factor_authentication")
            if tfa.verify_totp(current_user.totp_secret, form.code.data):
                session[SESSION_KEY_TFA_VERIFIED] = True
                next_page = safe_redirect_target(
                    request.args.get("next"), url_for(".index")
                )
                return redirect(next_page)
            flash("Invalid code", "error")

        return self.render("user/verify_tfa.html", form=form)

    @login_required
    @expose_url("/change_password/", methods=("GET", "POST"))
    def change_password(self):
        form = ChangePasswordForm()
        if form.validate_on_submit():
            current_userstore.user_set(
                current_user,
                password=current_user.hash_password(form.new_password.data),
            )
            flash("Password has been updated", "success")
            login_user(current_user)
            return redirect(url_for(".index"))

        return self.render("user/change_password.html", form=form)

    @expose_url("/forgot_password/", methods=("GET", "POST"))
    def forgot_password(self):
        if current_user.is_authenticated:
            return redirect(url_for(".index"))
        form = ForgotPasswordForm()
        if form.validate_on_submit():
            user = current_userstore.get_user_by_identity(form.email.data, "email")
            if user is not None and user.email_verified:
                current_security.get_plugin("reset_password").send_token(user)
            flash(
                "An email has been sent with instructions to reset your password.",
                "success",
            )
            return redirect(url_for(".login"))
        return self.render("user/forgot_password.html", form=form)

    @expose_url("/reset_password/", methods=("GET", "POST"))
    def reset_password(self):
        token = request.args.get("token")
        form = ResetPasswordForm()
        if form.validate_on_submit():
            try:
                current_security.get_plugin("reset_password").execute_with_token(
                    token, password=form.password.data
                )
            except TokenActionError:
                flash("The reset password link is invalid or has expired.", "error")
            else:
                flash("Your password has been reset.", "success")
                return redirect(url_for(".login"))
        return self.render("user/reset_password.html", form=form)

    @login_required
    @expose_url("/recovery_codes/")
    def recovery_codes(self):
        if (
            not current_user.tfa_enabled
            or not session.get(SESSION_KEY_TFA_VERIFIED)
        ):
            abort(403)
        recovery_codes = self._generate_recovery_codes(current_user)
        return self.render(
            "user/recovery_codes.html",
            recovery_codes=recovery_codes,
            _headers=NO_CACHE_HEADER,
        )

    def _generate_recovery_codes(self, user):
        tfa = current_security.get_plugin("two_factor_authentication")
        recovery_codes = tfa.generate_recovery_codes()
        hashed_codes = [current_security.hasher.hash(code) for code in recovery_codes]
        current_userstore.user_set(user, recovery_codes=hashed_codes)
        return recovery_codes

    @login_required
    @expose_url("/recovery/", methods=("GET", "POST"))
    def recovery(self):
        if not current_user.tfa_enabled or session.get(SESSION_KEY_TFA_VERIFIED):
            abort(403)
        form = RecoveryForm()
        if form.validate_on_submit():
            matching_index = None
            for index, stored_code in enumerate(current_user.recovery_codes or []):
                if current_security.hasher.verify(form.code.data, stored_code) or (
                    compare_digest(form.code.data, stored_code)
                ):
                    matching_index = index
            if matching_index is not None:
                remaining_codes = list(current_user.recovery_codes or [])
                remaining_codes.pop(matching_index)
                tfa = current_security.get_plugin("two_factor_authentication")
                totp_secret = tfa.generate_totp_secret()
                current_userstore.user_set(
                    current_user,
                    recovery_codes=remaining_codes,
                    totp_secret=totp_secret,
                )
                session[SESSION_KEY_TFA_VERIFIED] = True
                recovery_codes = self._generate_recovery_codes(current_user)
                totp_uri = tfa.get_totp_uri(
                    totp_secret, current_user.username
                )
                return self.render(
                    "user/setup_tfa.html",
                    totp_uri=totp_uri,
                    totp_secret=totp_secret,
                    recovery_codes=recovery_codes,
                    _headers=NO_CACHE_HEADER,
                )
            else:
                flash("Invalid recovery code", "error")
        return self.render("user/recovery.html", form=form)
