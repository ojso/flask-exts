from flask_login import user_logged_out

from ..admin import View, expose_url
from ..extension_core.base import Extension
from ..proxies import current_security
from ..signals import user_registered


class IndexView(View):
    allow_access = True

    def __init__(
        self,
        name="Index",
        endpoint="index",
        url="/",
    ):
        super().__init__(
            name=name,
            endpoint=endpoint,
            url=url,
        )

    @expose_url("/")
    def index(self):
        return self.render("index.html")

    @expose_url("/admin/")
    def adminindex(self):
        return self.render("admin/index.html")


class StartupExtension(Extension):
    @property
    def name(self) -> str:
        return "startup"

    @property
    def dependencies(self):
        return ["admin"]

    def init_app(self, app):
        """Initialize Jinja2, Flask-Login, subscribe to signals and add admin views."""
        self.register_views(app)
        self.subscribe_signals(app)

    def register_views(self, app):
        admin = app.extensions["exts"].get_extension("admin").get_admin()
        admin.register_view(IndexView(), is_menu=False)

    def subscribe_signals(self, app):
        # user registered
        @user_registered.connect_via(app)
        def on_user_registered(sender, user, **extra):
            """Signal handler for user registration."""
            if user.email and not user.email_verified:
                current_security.get_plugin("email_verification").send_token(user)

        # logged out
        @user_logged_out.connect_via(app)
        def on_user_logged_out(sender, user, **extra):
            """Signal handler for user logout."""
