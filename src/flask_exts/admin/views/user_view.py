from flask import url_for
from flask import request
from flask import redirect
from flask import flash
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from ..wraps import expose
from ..view import BaseView
from ...forms.forms.user import LoginForm
from ...forms.forms.user import RegistrationForm


class UserView(BaseView):
    """
    Default administrative interface index page when visiting the ``/user/`` URL.
    """

    index_template = "admin/user/index.html"
    login_template = "admin/user/index.html"
    register_template = "admin/user/index.html"

    login_form = LoginForm

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

    @expose("/")
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for(".login"))

        return self.render(self.index_template)

    @expose("/login/", methods=("GET", "POST"))
    def login(self):
        if current_user.is_authenticated:
            return redirect(url_for(".index"))

        form = self.login_form()
        if form.validate_on_submit():
            user = form.get_user()
            login_user(user)
            if (
                user is None
                or user.password is None
                or not user.check_password(form.password.data)
            ):
                flash("Invalid username or password")
            elif login_user(user, remember=form.remember_me.data):
                flash("Logged in successfully.")
                next_page = request.args.get("next")
                if not next_page:
                    next_page = url_for("index")
                return redirect(next_page)
            else:
                flash("user is not active.")

        title = "login"
        link = (
            "<p>Don't have an account? <a href=\""
            + url_for(".register")
            + '">Click here to register.</a></p>'
        )
        return self.render(self.login_template, form=form, title=title, link=link)

    @expose("/register/", methods=("GET", "POST"))
    def register(self):
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        form = RegistrationForm()
        if form.validate_on_submit():
            username = form.username.data
            if len(username) < 6 or len(username) > 50:
                flash("用户名长度限制6-50.")
            elif not re.match("^[a-z][a-z0-9_]+", username):
                flash("用户名只能包含小写字母，数字，下划线，且字母开头，请重新输入")
            else:
                # user = User(username=username)
                user = User()
                form.populate_obj(user)

                # email 数据未验证前存储在data中
                # user.email = form.email.data
                user.data = {"unverified_email": form.email.data}
                user.set_password(form.password.data)
                # 目前默认激活，否则无法登录
                user.isactive = True
                db.session.add(user)
                db.session.commit()
                flash("Congratulations, you are now a registered user!")
                return redirect(url_for("user.login"))
                login_user(user)
                return redirect(url_for(".index"))

        title = "Register"
        link = (
            '<p>Already have an account? <a href="'
            + url_for(".login")
            + '">Click here to log in.</a></p>'
        )
        return self.render(self.register_template, form=form, link=link)

    @expose("/logout/")
    def logout(self):
        logout_user()
        return redirect(url_for("admin.index"))
