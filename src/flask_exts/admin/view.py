from functools import wraps
from flask import Blueprint
from flask import url_for
from flask import abort

from ..utils import prettify_class_name


def expose(url="/", methods=("GET",)):
    """
    Use this decorator to expose views in your view classes.

    :param url:
        Relative URL for the view
    :param methods:
        Allowed HTTP methods. By default only GET is allowed.
    """

    def wrap(f):
        if not hasattr(f, "_urls"):
            f._urls = []
        f._urls.append((url, methods))
        return f

    return wrap


def _wrap_view(f):
    """wrapping f with self._handle_view and self._run_view"""
    # Avoid wrapping view method twice
    if hasattr(f, "_wrapped"):
        return f

    @wraps(f)
    def inner(self, *args, **kwargs):
        # Check if piece is accessible
        abort = self._handle_view(f, **kwargs)
        if abort is not None:
            return abort
        # run view
        return self._run_view(f, *args, **kwargs)

    inner._wrapped = True

    return inner


class ViewMeta(type):
    """
    View metaclass.
    """

    def __init__(cls, classname, bases, fields):
        type.__init__(cls, classname, bases, fields)

        # Gather exposed views
        cls._urls = []
        cls._default_view = None

        for name in dir(cls):
            attr = getattr(cls, name)
            if hasattr(attr, "_urls"):
                # Collect methods
                for url, methods in attr._urls:
                    cls._urls.append((url, name, methods))
                    if url == "/":
                        cls._default_view = name
                # Wrap views
                setattr(cls, name, _wrap_view(attr))


class BaseView(metaclass=ViewMeta):
    """
    Base view.
    """

    def __init__(
        self,
        name=None,
        endpoint=None,
        url=None,
        template_folder=None,
        static_folder=None,
        static_url_path=None,
        menu_class_name=None,
        menu_icon_type=None,
        menu_icon_value=None,
        skip_check_auth = False,
    ):
        """
        Constructor.

        :param name:
            Name of this view. If not provided, will default to the class name.
        :param endpoint:
            Base endpoint name for the view. For example, if there's a view method called "index" and
            endpoint is set to "myadmin", you can use `url_for('myadmin.index')` to get the URL to the
            view method. Defaults to the class name in lower case.
        :param url:
            Base URL. If provided, affects how URLs are generated. For example, if the url parameter
            is "test", the resulting URL will look like "/admin/test/". If not provided, will
            use endpoint as a base url. However, if URL starts with '/', absolute path is assumed
            and '/admin/' prefix won't be applied.
        :param static_url_path:
            Static URL Path. If provided, this specifies the path to the static url directory.
        :param menu_class_name:
            Optional class name for the menu item.
        :param menu_icon_type:
            Optional icon. Possible icon types:
             - `bi` - Bootstrap icon
             - `image` - Image relative to Flask static directory
             - `image_url` - Image with full URL
        :param menu_icon_value:
            Icon name or URL, depending on `menu_icon_type` setting
        """
        self.name = name or self._prettify_class_name(self.__class__.__name__)
        self.endpoint = endpoint or self._get_endpoint()
        self.url = url
        self.template_folder = template_folder
        self.static_folder = static_folder
        self.static_url_path = static_url_path
        self.menu = None
        self.menu_class_name = menu_class_name
        self.menu_icon_type = menu_icon_type
        self.menu_icon_value = menu_icon_value
        self.skip_check_auth = skip_check_auth

        # Initialized from create_blueprint
        self.admin = None
        self.blueprint = None

        # Default view
        if self._default_view is None:
            raise Exception(
                "Attempted to instantiate admin view %s without default view"
                % self.__class__.__name__
            )

    def _get_endpoint(self):
        """
        Generate Flask endpoint name. By default converts class name to lower case if endpoint is
        not explicitly provided.
        """
        return self.__class__.__name__.lower()

    def _get_url_prefix(self):
        """
        Generate URL for the view. Override to change default behavior.
        """
        if self.url is None:
            url_prefix = self.admin.url.rstrip("/") + "/" + self.endpoint
        elif self.url.startswith("/"):
            # index_view.url which has already been set startswith("/")
            url_prefix = self.url
        else:
            url_prefix = self.admin.url.rstrip("/") + "/" + self.url

        return url_prefix

    def create_blueprint(self):
        """
        Create Flask blueprint.
        """
        # Generate URL
        self.url_prefix = self._get_url_prefix()

        # If we're working from the root of the site, set prefix to None
        if self.url_prefix == "/":
            self.url_prefix = None

        # Create blueprint and register rules
        self.blueprint = Blueprint(
            self.endpoint,
            __name__,
            url_prefix=self.url_prefix,
            template_folder=self.template_folder,
            static_folder=self.static_folder,
            static_url_path=self.static_url_path,
        )

        for url, name, methods in self._urls:
            self.blueprint.add_url_rule(url, name, getattr(self, name), methods=methods)

        return self.blueprint

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
        # Store self as admin_view
        kwargs["view"] = self

        return self.admin.render(template, **kwargs)

    def _prettify_class_name(self, name):
        """
        Split words in PascalCase string into separate words.

        :param name:
            String to prettify
        """
        return prettify_class_name(name)

    def is_accessible(self):
        """
        Override this method to add permission checks.

        It does not make any assumptions about the authentication system used in your application, so it is
        up to you to implement it.

        By default, it will allow access for everyone.
        """
        if self.skip_check_auth:
            return True
        return self.admin.access(view=self)

    def _handle_view(self, fn, **kwargs):
        """
        This method will be executed before calling any view method.

        It will execute the ``inaccessible_callback`` if the view is not accessible.

        :param fn:
            View function
        :param kwargs:
            View function arguments
        """
        if self.skip_check_auth:
            return
        if not self.admin.access(view=self, fn=fn):
            return self.inaccessible_callback(fn, **kwargs)

    def _run_view(self, fn, *args, **kwargs):
        """
        This method will run actual view function.

        While it is similar to _handle_view, can be used to change arguments that are passed to the view.

        :param fn:
            View function
        :param kwargs:
            Arguments
        """
        return fn(self, *args, **kwargs)

    def inaccessible_callback(self, fn, **kwargs):
        """
        Handle the response to inaccessible views.

        By default, it throw HTTP 403 error. Override this method to
        customize the behaviour.
        """
        return abort(403)
