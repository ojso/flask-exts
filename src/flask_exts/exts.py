from typing import Optional, List, Type
from .extension_registry import ExtensionRegistry
from .extension import Extension


class Exts:
    """
    Composable Flask-Exts extension manager.

    This class orchestrates initialization of Flask-Exts components
    using a registry-based composition pattern instead of the God Object
    pattern. It remains 100% backward compatible with existing code.

    Usage:
        # Basic usage (backward compatible)
        exts = Exts(app)

        # With selective extension loading
        exts = Exts(app, extensions=['database', 'template', 'admin'])

        # Add custom extensions
        exts.register_extension(MyCustomExtension)
    """

    def __init__(
        self,
        app=None,
        extensions: Optional[List[str]] = None,
        skip_missing: bool = False
    ):
        """
        Initialize Exts manager.

        Args:
            app: Flask application (optional, call init_app later if not provided)
            extensions: List of extension names to enable (None = enable all)
            skip_missing: Skip missing extensions without error

        Example:
            # Load all extensions
            exts = Exts(app)

            # Load specific extensions only
            exts = Exts(app, extensions=['database', 'template'])

            # Defer initialization
            exts = Exts()
            exts.init_app(app)
        """
        self.app = app
        self._registry = ExtensionRegistry()
        self._enabled_extensions = extensions
        self._skip_missing = skip_missing

        # Register default extensions
        self._register_default_extensions()

        # Initialize if app provided
        if app is not None:
            self.init_app(app, extensions, skip_missing)

    def _register_default_extensions(self) -> None:
        """Register all built-in extensions"""
        # Import here to avoid circular imports
        from .extensions.database_ext import DatabaseExtension
        from .extensions.babel_ext import BabelExtension
        from .extensions.template_ext import TemplateExtension
        from .extensions.email_ext import EmailExtension
        from .extensions.usercenter_ext import UserCenterExtension
        from .extensions.security_ext import SecurityExtension
        from .extensions.admin_ext import AdminExtension
        from .extensions.startup_ext import StartupExtension

        for ext_class in [
            DatabaseExtension,
            BabelExtension,
            TemplateExtension,
            EmailExtension,
            UserCenterExtension,
            SecurityExtension,
            AdminExtension,
            StartupExtension,
        ]:
            self._registry.register(ext_class)

    def register_extension(
        self,
        extension_class: Type[Extension],
        enable: bool = True
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
        self,
        app,
        extensions: Optional[List[str]] = None,
        skip_missing: bool = False
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
        enabled = extensions or self._enabled_extensions

        # Initialize all extensions
        self._registry.init_all(app, enabled, skip_missing)


    # Backward compatibility methods
    def get_db(self):
        """Get SQLAlchemy db instance (backward compatible)"""
        from .datastore.sqla import db
        return db

    def get_template(self):
        """Get Template extension (backward compatible)"""
        if hasattr(self, 'template'):
            return self.template
        template_ext = self._registry.get('template')
        return template_ext._template if template_ext else None

    def get_email(self):
        """Get Email extension (backward compatible)"""
        if hasattr(self, 'email'):
            return self.email
        email_ext = self._registry.get('email')
        return email_ext._email if email_ext else None

    def get_usercenter(self):
        """Get UserCenter extension (backward compatible)"""
        if hasattr(self, 'usercenter'):
            return self.usercenter
        usercenter_ext = self._registry.get('usercenter')
        return usercenter_ext._usercenter if usercenter_ext else None

    def get_security(self):
        """Get Security extension (backward compatible)"""
        if hasattr(self, 'security'):
            return self.security
        security_ext = self._registry.get('security')
        return security_ext._security if security_ext else None

    def get_admin(self):
        """Get Admin extension (backward compatible)"""
        if hasattr(self, 'admin'):
            return self.admin
        admin_ext = self._registry.get('admin')
        return admin_ext._admin if admin_ext else None

    # Modern API
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
