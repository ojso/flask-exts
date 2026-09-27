from .base import Extension
from .registry import ExtensionRegistry


class ExtensionManager:
    """
    Composable Flask-Exts extension manager.

    This class orchestrates initialization of registered extensions through a
    registry-based composition pattern. It keeps the extension lifecycle
    separate from the concrete extension implementations.

    Usage:
        exts = ExtensionManager(app)
        exts.register_extension(MyCustomExtension)
    """

    def __init__(
        self,
        app=None,
    ):
        """
        Initialize the extension manager.

        Args:
            app: Flask application (optional; call init_app later if not provided)

        Example:
            exts = ExtensionManager(app)
            exts = ExtensionManager()
            exts.init_app(app)
        """
        self.app = app
        self._registry = ExtensionRegistry()

        # Register default extension classes
        self.register_default_extensions()

        # Initialize if app provided
        if app is not None:
            self.init_app(app)

    def register_default_extensions(self) -> None:
        """Register all built-in extensions"""
        for ext_class in Extension.get_all().values():
            self._registry.register(ext_class)

    def register_extension(
        self, extension_class: type[Extension], enable: bool = True
    ) -> Extension:
        """
        Register a custom extension.

        Args:
            extension_class: Class inheriting from Extension
            enable: Whether to enable immediately

        Returns:
            Extension: Instance of registered extension

        Example:
            class MyExtension(Extension):
                @property
                def name(self) -> str:
                    return "my_ext"

                def init_app(self, app):
                    pass

            exts.register_extension(MyExtension)
        """
        ext = self._registry.register(extension_class)

        if enable and self.app:
            self._registry.init(ext.name, self.app)

        return ext


    def init_app(
        self, app
    ) -> None:
        """
        Initialize all registered extensions for a Flask application.

        Args:
            app: Flask application
        """
        self.app = app

        # Register extension in app
        if not hasattr(app, "extensions"):
            app.extensions = {}

        if "exts" in app.extensions:
            raise RuntimeError("Exts extension already initialized for this app")

        app.extensions["exts"] = self

        # Initialize all extensions
        self._registry.init_all(app)

    def get_extension(self, name: str) -> Extension | None:
        """
        Get extension by name (modern API).

        Args:
            name: Extension name

        Returns:
            Extension instance or None
        """
        return self._registry.get(name)

    def list_extensions(self, sorted_by_priority: bool = True) -> list[Extension]:
        """
        List all registered extensions (modern API).

        Args:
            sorted_by_priority: Sort by initialization priority

        Returns:
            List of extensions
        """
        return self._registry.get_all(sorted_by_priority)

    def is_extension_enabled(self, name: str) -> bool:
        """
        Check if extension is enabled.

        Args:
            name: Extension name

        Returns:
            bool: True if enabled
        """
        return self._registry.is_initialized(name)

    def shutdown(self) -> None:
        """
        Shutdown all extensions and cleanup resources.
        """
        self._registry.shutdown(self.app)
