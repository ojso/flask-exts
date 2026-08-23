from abc import ABC, abstractmethod
from typing import List, Optional


class Extension(ABC):
    """
    Base class for all Flask-Exts extensions.

    Implementations should:
    1. Provide a unique name
    2. Define priority for initialization order
    3. Declare dependencies on other extensions
    4. Implement init_app for Flask app initialization

    Example:
        class MyExtension(Extension):
            @property
            def name(self) -> str:
                return "my_ext"

            @property
            def priority(self) -> int:
                return 50  # Load after core extensions

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
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """
        Initialization priority.

        Lower values load first. Core extensions should use 10-20,
        standard extensions 30-40, custom extensions 50+.

        Returns:
            int: Priority value (0-100+)
        """
        pass

    @property
    def dependencies(self) -> List[str]:
        """
        List of extension names this extension depends on.

        Returns:
            List[str]: Names of required extensions
        """
        return []

    @property
    def optional_dependencies(self) -> List[str]:
        """
        List of extension names this extension optionally uses.

        Won't raise error if missing, but features may be limited.

        Returns:
            List[str]: Names of optional extensions
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
        pass

    def shutdown(self, app=None):
        """
        Optional cleanup when app context is destroyed.

        Args:
            app: Flask application instance (optional)
        """
        pass


class ExtensionError(Exception):
    """Base exception for extension-related errors"""
    pass


class ExtensionNotFoundError(ExtensionError):
    """Raised when required extension is not found"""
    pass


class ExtensionDependencyError(ExtensionError):
    """Raised when extension dependency cannot be satisfied"""
    pass


class ExtensionInitError(ExtensionError):
    """Raised when extension initialization fails"""
    pass
