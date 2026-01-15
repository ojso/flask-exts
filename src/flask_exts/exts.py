class Exts:
    """This is used to manager babel,template,admin, and so on..."""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def get_db(self):
        from .datastore.sqla import db

        return db

    def init_babel(self, app):
        from .babel import babel_init_app

        babel_init_app(app)

    def get_template(self):
        from .template.base import Template

        return Template()

    def get_email(self):
        from .email.base import Email

        return Email()

    def get_usercenter(self):
        from .usercenter.core import UserCenter

        return UserCenter()

    def get_security(self):
        from .security.core import Security

        return Security()

    def get_admin(self):
        from .admin.admin import Admin

        return Admin()

    def run_bootstrap(self, app):
        from .bootstrap.startup import run_bootstrap

        run_bootstrap(app)

    def init_app(self, app):
        self.app = app

        if not hasattr(app, "extensions"):
            app.extensions = {}

        if "exts" in app.extensions:
            raise Exception("exts extension already exists in app.extensions.")

        app.extensions["exts"] = self

        # init sqlalchemy db
        db = self.get_db()
        db.init_app(app)

        # init babel
        self.init_babel(app)

        # init template
        self.template = self.get_template()
        self.template.init_app(app)

        # init email
        self.email = self.get_email()
        self.email.init_app(app)

        # init usercenter
        self.usercenter = self.get_usercenter()
        self.usercenter.init_app(app)

        # init security
        self.security = self.get_security()
        self.security.init_app(app)

        # init admin
        self.admin = self.get_admin()
        self.admin.init_app(app)

        # at last, run bootstrap tasks
        self.run_bootstrap(app)
