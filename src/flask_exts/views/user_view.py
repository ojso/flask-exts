from flask import current_app, render_template_string
from flask import url_for
from flask import request
from flask import redirect
from flask import flash
from flask import abort
from flask import jsonify
from flask import session
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from ..admin import BaseView
from ..admin import expose
from ..forms.login import LoginForm
from ..forms.register import RegisterForm
from ..forms.change_password import ChangePasswordForm
from ..forms.forgot_password import ForgotPasswordForm
from ..forms.reset_password import ResetPasswordForm
from ..forms.two_factor import TwoFactorForm
from ..proxies import _userstore
from ..proxies import _security
from ..signals import user_registered


class UserView(BaseView):
    """
    Default administrative interface index page when visiting the ``/user/`` URL.
    """

    index_template = "views/user/index.html"
    list_template = "views/user/list.html"
    login_template = "views/user/login.html"
    register_template = "views/user/register.html"
    verify_email_template = "views/user/verify_email.html"

    def __init__(
        self,
        name="User",
        endpoint="user",
        url="/user",
        template_folder=None,
        static_folder=None,
        static_url_path=None,
        menu_class_name=None,
        menu_icon_type=None,
        menu_icon_value=None,
    ):
        super().__init__(
            name=name,
            endpoint=endpoint,
            url=url,
            template_folder=template_folder,
            static_folder=static_folder,
            static_url_path=static_url_path,
            menu_class_name=menu_class_name,
            menu_icon_type=menu_icon_type,
            menu_icon_value=menu_icon_value,
        )

    def allow(self, *args, **kwargs):
        return True

    def get_login_form_class(self):
        return LoginForm

    def get_register_form_class(self):
        return RegisterForm

    @login_required
    @expose("/")
    def index(self):
        return self.render(self.index_template)

    @expose("/login/", methods=("GET", "POST"))
    def login(self):
        if current_user.is_authenticated:
            return redirect(url_for(".index"))
        form = self.get_login_form_class()()
        if form.validate_on_submit():
            user, error = _userstore.login_user_by_username_password(
                form.username.data, form.password.data
            )
            if user is None:
                flash(error, "error")
                # form.username.errors.append(error)
            else:
                if hasattr(form, "remember_me"):
                    login_user(user, force=True, remember=form.remember_me.data)
                else:
                    login_user(user, force=True)
                next_page = request.args.get("next")
                # 2FA
                if user.tfa_enabled:
                    if next_page:
                        return redirect(url_for(".verify_tfa", next=next_page))
                    else:
                        return redirect(url_for(".verify_tfa"))
                if not next_page:
                    next_page = url_for(".index")
                return redirect(next_page)
        return self.render(self.login_template, form=form)

    @expose("/register/", methods=("GET", "POST"))
    def register(self):
        if current_user.is_authenticated:
            return redirect(url_for(".index"))
        form = self.get_register_form_class()()
        if form.validate_on_submit():
            user, error = _userstore.create_user(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            if user is None:
                flash(error)
            else:
                user_registered.send(current_app._get_current_object(), user=user)
                login_user(user, force=True)
                return redirect(url_for(".index"))

        return self.render(self.register_template, form=form)

    @expose("/logout/")
    def logout(self):
        logout_user()
        return redirect(url_for(".index"))

    @expose("/verify_email/")
    def verify_email(self):
        token = request.args.get("token")
        r = _security.email_verification.verify_email_with_token(token)
        return self.render(self.verify_email_template, result=r[0])

    @login_required
    @expose("/enable_tfa", methods=("GET", "POST"))
    def enable_tfa(self):
        enable = request.args.get("enable")
        if enable is None:
            return jsonify({"tfa_enabled": current_user.tfa_enabled})

        enable = False if str(enable).lower() in ["0", "false"] else True
        if current_user.tfa_enabled == enable:
            return jsonify({"tfa_enabled": current_user.tfa_enabled})

        form = TwoFactorForm()
        if form.validate_on_submit():
            if _security.tfa.verify_totp(current_user.totp_secret, form.code.data):
                _userstore.user_set(current_user, tfa_enabled=enable)
                if current_user.tfa_enabled and not session.get("tfa_verified"):
                    session["tfa_verified"] = True
                elif not current_user.tfa_enabled and "tfa_verified" in session:
                    session.pop("tfa_verified")
                    # clear totp_secret
                    _userstore.user_set(current_user, totp_secret=None)
            else:
                return jsonify({"error": "Invalid code"})
        return jsonify({"tfa_enabled": current_user.tfa_enabled})

    @login_required
    @expose("/setup_tfa")
    def setup_tfa(self):
        if current_user.tfa_enabled:
            return self.render(
                "views/user/setup_tfa.html",
            )
        if not current_user.totp_secret:
            _userstore.user_set(
                current_user, totp_secret=_security.tfa.generate_totp_secret()
            )
        totp_uri = _security.tfa.get_totp_uri(
            current_user.totp_secret, current_user.username
        )
        _headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        return self.render(
            "views/user/setup_tfa.html",
            totp_uri=totp_uri,
            totp_secret=current_user.totp_secret,
            _headers=_headers,
        )

    @login_required
    @expose("/verify_tfa", methods=("GET", "POST"))
    def verify_tfa(self):
        if request.method == "GET" and "modal" in request.args:
            action = request.args.get("action")
            return self.render(
                "views/user/verify_tfa_modal.html", form=TwoFactorForm(), action=action
            )
        if not current_user.tfa_enabled:
            abort(403)
        if session.get("tfa_verified"):
            abort(403)
        form = TwoFactorForm()
        if form.validate_on_submit():
            if _security.tfa.verify_totp(current_user.totp_secret, form.code.data):
                session["tfa_verified"] = True
                next_page = request.args.get("next")
                if not next_page:
                    next_page = url_for(".index")
                return redirect(next_page)
            else:
                flash("Invalid code", "error")
        return self.render("views/user/verify_tfa.html", form=form)

    @login_required
    @expose("/change_password", methods=("GET", "POST"))
    def change_password(self):
        form = ChangePasswordForm()
        if form.validate_on_submit():
            _userstore.user_set(
                current_user,
                password=current_user.hash_password(form.new_password.data),
            )
            flash("Password has been updated", "success")
            return redirect(url_for(".index"))

        return self.render("views/user/change_password.html", form=form)

    @expose("/forgot_password", methods=("GET", "POST"))
    def forgot_password(self):
        if current_user.is_authenticated:
            return redirect(url_for(".index"))
        form = ForgotPasswordForm()
        if form.validate_on_submit():
            _security.forgot_password.send_forgot_password_token(form.email.data)
            flash(
                "If the email is registered, you will receive a password reset email shortly.",
                "info",
            )
            return redirect(url_for(".login"))
        return self.render("views/user/forgot_password.html", form=form)

    @expose("/reset_password", methods=("GET", "POST"))
    def reset_password(self):
        token = request.args.get("token")
        form = ResetPasswordForm()
        if form.validate_on_submit():
            r = _security.forgot_password.set_password_with_token(
                token, form.password.data
            )
            if r:
                flash("Your password has been updated.", "success")
                return redirect(url_for(".login"))
        return self.render("views/user/reset_password.html", form=form)
