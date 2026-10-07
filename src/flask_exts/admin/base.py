from flask import (
    has_app_context,
    make_response,
    render_template,
    render_template_string,
    url_for,
)

from ..proxies import current_security
from .menu import Menu


class Admin:
    """
    Collection of the views. Also manages menu structure.
    """

    def __init__(self, app=None):
        self.app = app
        self.name = self.get_admin_name()
        self.url = self.get_admin_url()
        self.endpoint = self.get_admin_endpoint()
        self.template_folder = self.get_admin_template_folder()
        self.static_folder = self.get_admin_static_folder()
        self._views = {}
        self.menu = Menu(self)
        self.all_accessed = True
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Constructor.

        Args:
            app:
                Flask application object
            name:
                Application name. Will be displayed in the main menu and as a page title. Defaults to "Admin"
            url:
                Base URL
            endpoint:
                Base endpoint name for index view. If you use multiple instances of the `Admin` class with
                a single Flask application, you have to set a unique endpoint name for each instance.

        """
        self.app = app

        # Register views
        for v in self._views.values():
            app.register_blueprint(v.create_blueprint())

    def get_admin_name(self):
        name = "Admin"
        return name

    def get_admin_url(self):
        url = "/admin"
        if not url.startswith("/"):
            raise ValueError("admin.url must startswith /")
        return url

    def get_admin_endpoint(self):
        return "admin"

    def get_admin_template_folder(self):
        template_folder = "../templates"
        return template_folder

    def get_admin_static_folder(self):
        static_folder = "../static"
        return static_folder

    def register_view(self, view, is_menu=True, category=None):
        """
        Add a view to the collection.

        Args:
            view:
                View to add.
        """
        # attach self(admin) to view
        view.admin = self

        # Add to _views
        view_name = view.name.lower().replace(" ", "_")

        if view_name in self._views:
            raise ValueError(f"View with name {view.name} already exists")

        self._views[view_name] = view

        # If app was provided in constructor, register view with Flask app
        if self.app is not None:
            self.app.register_blueprint(view.create_blueprint())

        if is_menu:
            self.menu.add_view(view, category)

    def get_url(self, endpoint, **kwargs):
        """
        Generate URL for the endpoint.

        Args:
            endpoint:
                Flask endpoint name
            kwargs:
                Arguments for `url_for`
        """
        return url_for(endpoint, **kwargs)

    def allow(self, *args, **kwargs):
        if has_app_context():
            return current_security.authorize_allow(*args, **kwargs)
        return True

    def render(self, template, **kwargs):
        """
        Render template

        Args:
            template:
                Template path to render
            kwargs:
                Template arguments
        """
        # Add admin instance to kwargs
        kwargs["admin"] = self
        # Add URL generation method to kwargs
        kwargs["get_url"] = self.get_url

        # If _headers is provided in kwargs, use make_response to set headers
        if "_headers" in kwargs:
            headers = kwargs.pop("_headers")
            response = make_response(render_template(template, **kwargs))
            for key, value in headers.items():
                response.headers[key] = value
            return response
        else:
            return render_template(template, **kwargs)

    def render_string(self, source, **kwargs):
        """
        Render source string as template

        Args:
            source:
                Source string to render as template
            kwargs:
                Template arguments
        """
        # Add admin instance to kwargs
        kwargs["admin"] = self
        # Add URL generation method to kwargs
        kwargs["get_url"] = self.get_url

        return render_template_string(source, **kwargs)
