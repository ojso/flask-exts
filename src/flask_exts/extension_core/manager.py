from .base import Extension
from .registry import ExtensionRegistry


class ExtensionManager:
    """Composable Flask-Exts extension manager.

    This class orchestrates initialization of registered extensions through a
    registry-based composition pattern. It keeps the extension lifecycle
    separate from the concrete extension implementations: initialization runs
    in two neutral phases (``init_app`` then ``post_init``) and the manager
    never references a specific extension by name.

    Examples:
        exts = ExtensionManager(app)
        exts.register_extension(MyCustomExtension)
    """

    def __init__(
        self,
        app=None,
        register_builtin=True,
    ):
        """Initialize the extension manager.

        Args:
            app: Flask application (optional; call init_app later if not provided)

        Examples:
            exts = ExtensionManager(app)

            exts = ExtensionManager()
            exts.init_app(app)

            exts = ExtensionManager(register_builtin=False)
        """
        self.app = app
        self._registry = ExtensionRegistry()

        # Register built-in extensions
        if register_builtin:
            from ..builtin_extensions import BUILTIN_EXTENSIONS

            for ext_class in BUILTIN_EXTENSIONS:
                self.register_extension(ext_class)

        # Initialize if app provided
        if app is not None:
            self.init_app(app)

    def get_registry(self) -> ExtensionRegistry:
        """Get the underlying extension registry.

        Returns:
            ExtensionRegistry: The registry instance
        """
        return self._registry

    def register_extension(self, extension_class: type[Extension]) -> Extension:
        """Register a custom extension.

        Args:
            extension_class: Class inheriting from Extension

        Returns:
            Extension: Instance of registered extension

        Note:
            If the manager already has an app (``init_app`` already ran),
            this immediately runs both lifecycle phases -- ``init_app`` then
            ``post_init`` -- for the new extension alone. It will not,
            however, retroactively re-run other extensions' ``post_init`` to
            pick up a newly added contribution (e.g. a late-registered
            ``AdminViewMixin`` provider will not be seen by an admin whose
            own ``post_init`` already ran).

        Examples:
            class MyExtension(Extension):
                @property
                def name(self) -> str:
                    return "my_ext"

                def init_app(self, app):
                    pass

            exts.register_extension(MyExtension)
        """
        ext = self._registry.register(extension_class)

        # Late registration (after init_app already ran) goes through the
        # same registry entry points as the bulk path, so init/post_init
        # bookkeeping (idempotency, the "init before post_init" guard) stays
        # consistent regardless of when an extension was added.
        if self.app:
            self._registry.init(ext.name, self.app)
            self._registry.post_init(ext.name, self.app)

        return ext

    def init_app(self, app) -> None:
        """Initialize all registered extensions for a Flask application.

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

        # Phase 1: every extension builds its own services
        self._registry.init_all(app)

        # Phase 2: extensions wire into each other, now that every peer
        # exists. The manager stays agnostic of what any of them do here.
        self._registry.post_init_all(app)

    def shutdown(self) -> None:
        """Shutdown all extensions and cleanup resources."""
        self._registry.shutdown_all()

    def get_extension(self, name: str) -> Extension | None:
        """Get extension by name (modern API).

        Args:
            name: Extension name

        Returns:
            Extension instance or None
        """
        return self._registry.get_extension(name)

    def list_extensions(self) -> list[Extension]:
        """List all registered extensions (modern API).

        Args:
            sorted_by_priority: Sort by initialization priority

        Returns:
            List of extensions
        """
        return self._registry.list_extensions()

    def has_extension(self, name: str) -> bool:
        """Check if extension is enabled.

        Args:
            name: Extension name

        Returns:
            bool: True if enabled
        """
        return self._registry.is_initialized(name)
