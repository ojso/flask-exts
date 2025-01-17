from .babel import babel_init_app
from .template import template_init_app
from .users import user_init_app
from .admin import Admin
from .views.index_view import IndexView
from .views.user_view import UserView


class Manager:
    """This is used to manager babel,form,admin."""

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

        if not hasattr(app, "extensions"):
            app.extensions = {}

        if app.config.get("BABEL_ENABLED", True) and "babel" not in app.extensions:
            babel_init_app(app)

        if (
            app.config.get("TEMPLATE_ENABLED", True)
            and "template" not in app.extensions
        ):
            template_init_app(app)

        if app.config.get("USER_ENABLED", True) and "user" not in app.extensions:
            user_init_app(app)

        if app.config.get("ADMIN_ENABLED", True):
            # Admin init for index_view and user_view
            admin_index_view = app.config.get("ADMIN_INDEX_VIEW", IndexView())
            admin_user_view = app.config.get("ADMIN_USER_VIEW", UserView())
            admin = Admin(index_view=admin_index_view, user_view=admin_user_view)
            admin.init_app(app)
