from flask import url_for
from flask import request
from flask import redirect
from flask import flash
from flask import abort
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from ...utils.form import validate_form_on_submit
from ..wraps import expose
from ..view import BaseView
from flask import current_app


class UserView(BaseView):
    """
    Default administrative interface index page when visiting the ``/user/`` URL.
    """

    index_template = "admin/user/index.html"
    list_template = "admin/user/list.html"
    login_template = "admin/user/login.html"
    register_template = "admin/user/register.html"

    def __init__(
        self,
        name="User",
        category=None,
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
            category=category,
            endpoint=endpoint,
            url=url,
            template_folder=template_folder,
            static_folder=static_folder,
            static_url_path=static_url_path,
            menu_class_name=menu_class_name,
            menu_icon_type=menu_icon_type,
            menu_icon_value=menu_icon_value,
        )

    @property
    def usercenter(self):
        return current_app.extensions["usercenter"]

    def get_login_form_class(self):
        return self.usercenter.login_form_class

    def get_register_form_class(self):
        return self.usercenter.register_form_class

    def get_users(self):
        return self.usercenter.get_users()

    def validate_login_and_get_user(self, form):
        (user, error) = self.usercenter.login_user_by_username_password(
            form.username.data, form.password.data
        )
        return (user, error)

    def validate_register_and_create_user(self, form):
        (user, error) = self.usercenter.register_user(
            form.username.data, form.password.data, form.email.data
        )
        return (user, error)

    @login_required
    @expose("/")
    def index(self):
        return self.render(self.index_template)

    @login_required
    @expose("/list/")
    def list(self):
        if "admin" in current_user.get_roles():
            users = self.get_users()
            return self.render(self.list_template, users=users)
        else:
            abort(405)

    @expose("/login/", methods=("GET", "POST"))
    def login(self):
        if current_user.is_authenticated:
            return redirect(url_for(".index"))
        form = self.get_login_form_class()()
        if validate_form_on_submit(form):
            (user, error) = self.validate_login_and_get_user(form)
            if user is None:
                flash(error)
            else:
                if hasattr(form, "remember_me"):
                    login_user(user, remember=form.remember_me.data)
                else:
                    login_user(user)
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
        if validate_form_on_submit(form):
            (user, error) = self.validate_register_and_create_user(form)
            if user is None:
                flash(error)
            else:
                login_user(user)
                return redirect(url_for(".index"))

        return self.render(self.register_template, form=form)

    @expose("/logout/")
    def logout(self):
        logout_user()
        return redirect(url_for("index.index"))
