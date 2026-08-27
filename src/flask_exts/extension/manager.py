from typing import Optional, List, Type
from .base import Extension
from .registry import ExtensionRegistry
from ..extensions import *


class ExtensionManager:
    """
    Composable Flask-Exts extension manager.

    This class orchestrates initialization of Flask-Exts components
    using a registry-based composition pattern instead of the God Object
    pattern. It remains 100% backward compatible with existing code.

    Usage:
        # Basic usage (backward compatible)
        exts = ExtensionManager(app)

        # With selective extension loading
        exts = ExtensionManager(app, extensions=['database', 'template', 'admin'])

        # Add custom extensions
        exts.register_extension(MyCustomExtension)
    """

    def __init__(
        self,
        app=None,
        extensions: Optional[List[str]] = None,
        skip_missing: bool = False,
    ):
        """
        Initialize Exts manager.

        Args:
            app: Flask application (optional, call init_app later if not provided)
            extensions: List of extension names to enable (None = enable all)
            skip_missing: Skip missing extensions without error

        Example:
            # Load all extensions
            exts = ExtensionManager(app)

            # Load specific extensions only
            exts = ExtensionManager(app, extensions=['database', 'template'])

            # Defer initialization
            exts = ExtensionManager()
            exts.init_app(app)
        """
        self.app = app
        self._registry = ExtensionRegistry()
        self._enabled_extensions = None
        self._skip_missing = skip_missing

        # Register default extension classes
        self.register_default_extensions()

        # Initialize if app provided
        if app is not None:
            self.init_app(app, extensions, skip_missing)

    def register_default_extensions(self) -> None:
        """Register all built-in extensions"""
        for _, ext_class in Extension.get_exts().items():
            self._registry.register(ext_class)

    def register_extension(
        self, extension_class: Type[Extension], enable: bool = True
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

    def enable_extension(self, name: str) -> None:
        """
        Enable an extension.

        Args:
            name: Extension name
        """
        if self._enabled_extensions is None:
            self._enabled_extensions = []
        if name not in self._enabled_extensions:
            self._enabled_extensions.append(name)

    def disable_extension(self, name: str) -> None:
        """
        Disable an extension.

        Args:
            name: Extension name
        """
        if self._enabled_extensions and name in self._enabled_extensions:
            self._enabled_extensions.remove(name)

    def init_app(
        self, app, extensions: Optional[List[str]] = None, skip_missing: bool = False
    ) -> None:
        """
        Initialize extensions with Flask application.

        Args:
            app: Flask application
            extensions: Extension names to enable (None = use init time setting or all)
            skip_missing: Skip missing extensions without error
        """
        self.app = app

        # Register extension in app
        if not hasattr(app, "extensions"):
            app.extensions = {}

        if "exts" in app.extensions:
            raise RuntimeError("Exts extension already initialized for this app")

        app.extensions["exts"] = self

        # Determine which extensions to enable
        enabled = self._enabled_extensions

        # Initialize all extensions
        self._registry.init_all(app, enabled, skip_missing)

    def get_extension(self, name: str) -> Optional[Extension]:
        """
        Get extension by name (modern API).

        Args:
            name: Extension name

        Returns:
            Extension instance or None
        """
        return self._registry.get(name)

    def list_extensions(self, sorted_by_priority: bool = True) -> List[Extension]:
        """
        List all registered extensions (modern API).

        Args:
            sorted_by_priority: Sort by initialization priority

        Returns:
            List of extensions
        """
        return self._registry.list(sorted_by_priority)

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
