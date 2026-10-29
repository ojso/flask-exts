from abc import ABC, abstractmethod


class Extension(ABC):
    """
    Base class for all Flask-Exts extensions.

    Lifecycle, in order:

    1. ``init_app(app)``  -- build this extension's own services. Other
       extensions may not be initialized yet, so do not reach for them here.
    2. ``post_init(app)`` -- optional second pass, run only after every
       registered extension has finished ``init_app``. Use this to look up
       and wire into other extensions.
    3. ``shutdown()``     -- release resources, run in reverse order.

    The two-phase split keeps the core neutral: it never needs to know which
    concrete extensions exist or in what order they were registered relative
    to each other. An extension that wants to collect contributions from its
    peers (for example, admin collecting views) does so in its own
    ``post_init`` by inspecting the registry -- see ``admin.AdminViewMixin``
    for the convention this project uses for that.

    Example:
        class MyExtension(Extension):
            @property
            def name(self) -> str:
                return "my_ext"

            def init_app(self, app):
                # Initialize extension with app
                pass
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique identifier for this extension.

        Returns:
            str: Extension name (lowercase, no spaces)
        """
        ...

    @property
    def dependencies(self) -> list[str]:
        """
        List of extension names this extension depends on.

        Returns:
            list[str]: Names of required extensions
        """
        return []

    @abstractmethod
    def init_app(self, app):
        """
        Initialize extension with Flask application.

        Args:
            app: Flask application instance

        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If dependencies are missing
        """
        ...

    def post_init(self, app):
        """
        Second initialization phase, run after every extension's ``init_app``.

        Optional hook. Override to wire into other extensions once the whole
        registry is guaranteed to be initialized -- regardless of
        registration order.

        Args:
            app: Flask application instance
        """

    def shutdown(self):
        """
        Optional cleanup when app context is destroyed.

        Args:
            app: Flask application instance (optional)
        """


class ExtensionError(Exception):
    """Base exception for extension-related errors"""


class ExtensionNotFoundError(ExtensionError):
    """Raised when required extension is not found"""


class ExtensionDependencyError(ExtensionError):
    """Raised when extension dependency cannot be satisfied"""


class ExtensionInitError(ExtensionError):
    """Raised when extension initialization fails"""
