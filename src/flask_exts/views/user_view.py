from flask import current_app
from flask import url_for
from flask import request
from flask import redirect
from flask import flash
from flask import abort
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from ..admin import BaseView
from ..admin import expose
from ..forms.login import LoginForm
from ..forms.register import RegisterForm
from ..proxies import _usercenter
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

    def get_users(self):
        return _usercenter.get_users()

    def validate_login_and_get_user(self, form):
        user, error = _usercenter.login_user_by_username_password(
            form.username.data, form.password.data
        )
        return user, error

    def validate_register_and_create_user(self, form):
        user, error = _usercenter.create_user(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
        )
        return user, error

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
            user, error = self.validate_login_and_get_user(form)
            if user is None:
                flash(error, "error")
                # form.username.errors.append(error)
            else:
                if hasattr(form, "remember_me"):
                    login_user(user, force=True, remember=form.remember_me.data)
                else:
                    login_user(user, force=True)
                next_page = request.args.get("next")
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
            user, error = self.validate_register_and_create_user(form)
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
        r = _security.email_verification.verify_email_token(token)
        return self.render(self.verify_email_template, result=r[0])
