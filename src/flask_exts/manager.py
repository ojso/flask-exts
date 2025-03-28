class Manager:
    """This is used to manager babel,template,admin, and so on..."""

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

        if not hasattr(app, "extensions"):
            app.extensions = {}

        if app.config.get("DB_ENABLED", True):
            from .datastore import init_db

            if not app.config.get("SQLALCHEMY_DATABASE_URI", None):
                app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
            init_db(app)

        if app.config.get("BABEL_ENABLED", True) and "babel" not in app.extensions:
            from .babel import babel_init_app

            babel_init_app(app)

        if (
            app.config.get("TEMPLATE_ENABLED", True)
            and "template" not in app.extensions
        ):
            from .template import template_init_app

            template_init_app(app)

        if app.config.get("SECURITY_ENABLED", True) and "security" not in app.extensions:
            from .security import security_init_app

            security_init_app(app)

        if app.config.get("USER_ENABLED", True) and "user" not in app.extensions:
            from .users import user_init_app

            user_init_app(app)

        if app.config.get("ADMIN_ENABLED", True):
            from .admin import Admin

            admin = Admin()
            admin.init_app(app)

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
