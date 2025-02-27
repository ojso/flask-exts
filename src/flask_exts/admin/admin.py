from flask import render_template
from flask import url_for
from .menu import Menu


class Admin:
    """
    Collection of the admin views. Also manages menu structure.
    """

    def __init__(
        self,
        app=None,
        name="Admin",
        url="/admin",
        endpoint="admin",
        template_folder=None,
        static_folder=None,
    ):
        """
        Constructor.

        :param app:
            Flask application object
        :param name:
            Application name. Will be displayed in the main menu and as a page title. Defaults to "Admin"
        :param url:
            Base URL
        :param endpoint:
            Base endpoint name for index view. If you use multiple instances of the `Admin` class with
            a single Flask application, you have to set a unique endpoint name for each instance.

        """
        self.app = app
        self.name = name
        self.endpoint = endpoint
        self.url = url
        if not self.url.startswith("/"):
            raise ValueError("admin.url must startswith /")
        self.template_folder = template_folder or "../templates"
        self.static_folder = static_folder or "../static"
        self._views = []
        self.menu = Menu(self)
        # Register with application
        if app is not None:
            self._init_extension()

    def add_view(self, view, is_menu=True, category=None):
        """
        Add a view to the collection.

        :param view:
            View to add.
        """
        # attach self(admin) to view
        view.admin = self

        # Add to views
        self._views.append(view)

        # If app was provided in constructor, register view with Flask app
        if self.app is not None:
            self.app.register_blueprint(view.create_blueprint())

        if is_menu:
            self.menu.add_view(view, category)

    def get_url(self, endpoint, **kwargs):
        """
        Generate URL for the endpoint. If you want to customize URL generation
        logic (persist some query string argument, for example), this is
        right place to do it.

        :param endpoint:
            Flask endpoint name
        :param kwargs:
            Arguments for `url_for`
        """
        return url_for(endpoint, **kwargs)

    def render(self, template, **kwargs):
        """
        Render template

        :param template:
            Template path to render
        :param kwargs:
            Template arguments
        """
        # Store self as admin
        kwargs["admin"] = self
        # Expose get_url helper
        kwargs["get_url"] = self.get_url

        return render_template(template, **kwargs)

    def init_app(self, app):
        """
        Register all views with the Flask application.

        :param app:
            Flask application instance
        """
        self.app = app
        self._init_extension()

        # Register views
        for view in self._views:
            app.register_blueprint(view.create_blueprint())

    def _init_extension(self):
        admins = self.app.extensions.get("admin", [])

        for p in admins:
            if p.endpoint == self.endpoint:
                raise Exception(
                    "Cannot have two Admin() instances with same endpoint name."
                )

            if p.url == self.url:
                raise Exception("Cannot assign two Admin() instances with same URL.")

        admins.append(self)
        self.app.extensions["admin"] = admins
