from flask import url_for
from flask import request
from flask import redirect
from flask import flash
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from ...utils.form import validate_form_on_submit
from ..wraps import expose
from ..view import BaseView
from flask import current_app


class UserView(BaseView):
    """
    Default administrative interface index page when visiting the ``/user/`` URL.
    """

    index_template = "admin/user/index.html"
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

    def create_user(self, form):
        raise NotImplementedError()

    def validate_register(self, form):
        """validate submit form"""
        raise NotImplementedError()

    @expose("/")
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for(".login"))

        return self.render(self.index_template)

    @expose("/login/", methods=("GET", "POST"))
    def login(self):
        if current_user.is_authenticated:
            return redirect(url_for(".index"))

        usercenter = current_app.extensions["usercenter"]

        form = usercenter.login_form_class()
        if validate_form_on_submit(form):

            user = usercenter.get_user_by_username(form.username.data)
            if user is None:
                flash("not found user")
            elif not usercenter.validate_login(form.username.data, form.password.data):
                flash("Invalid username or password")
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

        usercenter = current_app.extensions["usercenter"]

        form = usercenter.register_form_class()
        if validate_form_on_submit(form):
            if self.validate_register(form):
                user = self.create_user(form)
                if user is not None:
                    login_user(user)
                    return redirect(url_for(".index"))

        return self.render(self.register_template, form=form)

    @expose("/logout/")
    def logout(self):
        logout_user()
        return redirect(url_for("admin.index"))
