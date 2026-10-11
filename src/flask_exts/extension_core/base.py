from abc import ABC, abstractmethod

from ..admin import View


class Extension(ABC):
    """
    Base class for all Flask-Exts extensions.

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

    def get_admin_views(self) -> list[tuple[View, bool]]:
        """
        Views this extension wants registered on the admin instance.
        Returns a list of (view_instance, is_menu) tuples.
        """
        return []

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
