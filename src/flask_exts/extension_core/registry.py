from .base import (
    Extension,
    ExtensionDependencyError,
    ExtensionError,
    ExtensionInitError,
    ExtensionNotFoundError,
)


class ExtensionRegistry:
    """
    Manages registration and initialization of Flask-Exts extensions.

    Features:
    - Dynamic registration and discovery
    - Dependency resolution
    - Priority-based initialization order
    - Circular dependency detection

    Example:
        registry = ExtensionRegistry()
        registry.register(DatabaseExtension)
        registry.register(TemplateExtension)
        registry.init_all(app)
    """

    def __init__(self):
        """Initialize empty registry"""
        self._extension_classes: dict[str, type[Extension]] = {}
        self._instances: dict[str, Extension] = {}
        self._initialized: set[str] = set()

    def register(self, extension_class: type[Extension]) -> Extension:
        """
        Register an extension class.

        Args:
            extension_class: Class inheriting from Extension

        Returns:
            Extension: Instance of the registered extension

        Raises:
            ExtensionError: If extension is invalid or name conflicts
        """
        if not issubclass(extension_class, Extension):
            raise ExtensionError(f"{extension_class} must inherit from Extension")

        # Instantiate to get name
        ext = extension_class()
        name = ext.name

        # Check for duplicates
        if name in self._extension_classes:
            raise ExtensionError(f"Extension '{name}' already registered")

        # Validate name
        if not name or not name.isascii() or not name.replace("_", "").isalnum():
            raise ExtensionError(f"Invalid extension name: '{name}'")

        self._extension_classes[name] = extension_class
        self._instances[name] = ext

        return ext

    def unregister(self, name: str) -> bool:
        """
        Unregister an extension (mainly for testing).

        Args:
            name: Extension name

        Returns:
            bool: True if unregistered, False if not found
        """
        if name in self._extension_classes:
            del self._extension_classes[name]
            if name in self._instances:
                del self._instances[name]
            if name in self._initialized:
                self._initialized.discard(name)
            return True
        return False

    def get_extension(self, name: str) -> Extension | None:
        """
        Get extension instance by name.

        Args:
            name: Extension name

        Returns:
            Extension instance or None if not found
        """
        return self._instances.get(name)

    def list_extensions(self) -> list[Extension]:
        """
        Get all registered extensions.

        Returns:
            list[Extension]: Registered extensions
        """
        extensions = [self._instances[name] for name in self.initialization_order()]

        return extensions

    def initialization_order(self) -> list[str]:
        """
        Return extension names in dependency-respecting order.

        Extensions with no dependency relationship between them keep registration
        order, so the result is deterministic and does not depend on dict/set
        iteration internals.

        Raises:
            ExtensionNotFoundError: a declared dependency is not registered
            ExtensionDependencyError: dependency graph contains a cycle
        """
        names = list(self._instances)
        order: list[str] = []
        done: set[str] = set()
        in_progress: list[str] = []

        def visit(name: str) -> None:
            if name in done:
                return
            if name in in_progress:
                cycle = " -> ".join(in_progress[in_progress.index(name) :] + [name])
                raise ExtensionDependencyError(f"Circular dependency detected: {cycle}")

            in_progress.append(name)
            for dep in self._instances[name].dependencies:
                if dep not in self._instances:
                    raise ExtensionNotFoundError(
                        f"Extension '{name}' requires '{dep}' which is not registered"
                    )
                visit(dep)
            in_progress.pop()

            done.add(name)
            order.append(name)

        for name in names:
            visit(name)

        return order

    def init_all(self, app) -> None:
        """
        Initialize all registered extensions in priority order.

        Args:
            app: Flask application

        Raises:
            ExtensionDependencyError: If dependencies not satisfied
            ExtensionInitError: If initialization fails
        """
        for name in self.initialization_order():
            self.init(name, app)

    def shutdown_all(self) -> None:
        """
        Shutdown all extensions in reverse order.

        Args:
            app: Flask application (optional)
        """
        for name in reversed(self.initialization_order()):
            ext = self.get_extension(name)
            try:
                ext.shutdown()
            except ExtensionError as e:
                # Log but don't raise during shutdown
                import warnings

                warnings.warn(f"Error shutting down {ext.name}: {e}")
            self._initialized.discard(name)

    def init(self, name: str, app) -> None:
        """
        Initialize a single extension by name.

        Args:
            name: Extension name
            app: Flask application

        Raises:
            ExtensionNotFoundError: If extension not found
            ExtensionInitError: If initialization fails
        """

        if name in self._initialized:
            return

        ext = self.get_extension(name)

        # Check if all dependencies of an extension are available.
        for dep in ext.dependencies:
            if not self.is_initialized(dep):
                raise ExtensionDependencyError(
                    f"Extension '{ext.name}' requires '{dep}' which is not initialized"
                )

        ext.init_app(app)
        self._initialized.add(name)

    def is_initialized(self, name: str) -> bool:
        """
        Check if an extension is initialized.

        Args:
            name: Extension name

        Returns:
            bool: True if initialized
        """
        return name in self._initialized
