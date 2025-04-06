from .datastore.sqla import sqldb_init_app
from .babel import babel_init_app
from .template import template_init_app
from .security import security_init_app
from .utils.authorize import authorize_allow
from .admin import Admin


class Manager:
    """This is used to manager babel,template,admin, and so on..."""

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

        if not hasattr(app, "extensions"):
            app.extensions = {}

        # config extends
        if app.config.get("SQLALCHEMY_DATABASE_URI", None) is None:
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        else:
            app.config["SQLALCHEMY_USERCENTER"] = True

        # init db
        if "sqlalchemy" not in app.extensions:
            sqldb_init_app(app)

        if "babel" not in app.extensions:
            babel_init_app(app)

        if "template" not in app.extensions:
            template_init_app(app)

        if "security" not in app.extensions:
            security_init_app(app)

        admin = Admin()
        admin.init_app(app)

        if app.config.get("ADMIN_ACCESS_ENABLED", True):
            admin.set_access_callback(authorize_allow)

        if "ADMIN_INDEX_VIEW" in app.config:
            admin_index_view = app.config.get("ADMIN_INDEX_VIEW")
        else:
            from .views.index_view import IndexView

            admin_index_view = IndexView()
        if admin_index_view:
            admin.add_view(admin_index_view, is_menu=False)

        if "ADMIN_USER_VIEW" in app.config:
            admin_user_view = app.config.get("ADMIN_USER_VIEW")
        else:
            from .views.user_view import UserView

            admin_user_view = UserView()
        if admin_user_view:
            admin.add_view(admin_user_view, is_menu=False)
