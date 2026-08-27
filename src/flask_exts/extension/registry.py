from typing import Dict, List, Optional, Set, Type
from .base import (
    Extension,
    ExtensionError,
    ExtensionNotFoundError,
    ExtensionDependencyError,
    ExtensionInitError,
)


class ExtensionRegistry:
    """
    Manages registration and initialization of Flask-Exts extensions.

    Features:
    - Dynamic registration and discovery
    - Dependency resolution
    - Priority-based initialization order
    - Selective extension loading
    - Circular dependency detection

    Example:
        registry = ExtensionRegistry()
        registry.register(DatabaseExtension)
        registry.register(TemplateExtension)
        registry.init_all(app)

        # Or selectively load
        registry.init_all(app, enabled=['database', 'template'])
    """

    def __init__(self):
        """Initialize empty registry"""
        self._extension_classes: Dict[str, Type[Extension]] = {}
        self._instances: Dict[str, Extension] = {}
        self._initialized: Set[str] = set()

    def register(self, extension_class: Type[Extension]) -> Extension:
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
        if not name or not name.replace("_", "").isalnum():
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

    def get(self, name: str) -> Optional[Extension]:
        """
        Get extension instance by name.

        Args:
            name: Extension name

        Returns:
            Extension instance or None if not found
        """
        return self._instances.get(name)

    def list(self, sorted_by_priority: bool = True) -> List[Extension]:
        """
        Get all registered extensions.

        Args:
            sorted_by_priority: If True, sort by priority

        Returns:
            List[Extension]: Registered extensions
        """
        extensions = list(self._instances.values())

        if sorted_by_priority:
            extensions.sort(key=lambda e: e.priority)

        return extensions

    def _check_dependencies(
        self, name: str, enabled: Optional[List[str]] = None
    ) -> None:
        """
        Check if all dependencies of an extension are available.

        Args:
            name: Extension name
            enabled: List of enabled extension names

        Raises:
            ExtensionDependencyError: If dependencies not satisfied
        """
        ext = self.get(name)
        if not ext:
            return

        # Check required dependencies
        for dep in ext.dependencies:
            if not self.get(dep):
                raise ExtensionDependencyError(
                    f"Extension '{name}' requires '{dep}' which is not registered"
                )

            if enabled and dep not in enabled:
                raise ExtensionDependencyError(
                    f"Extension '{name}' requires '{dep}' which is not enabled"
                )

    def _detect_circular_dependencies(self) -> None:
        """
        Detect circular dependencies between extensions.

        Raises:
            ExtensionDependencyError: If circular dependency detected
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def visit(name: str, path: List[str]) -> None:
            visited.add(name)
            rec_stack.add(name)

            ext = self.get(name)
            if ext:
                for dep in ext.dependencies:
                    if dep not in visited:
                        visit(dep, path + [name])
                    elif dep in rec_stack:
                        cycle = " -> ".join(path + [name, dep])
                        raise ExtensionDependencyError(
                            f"Circular dependency detected: {cycle}"
                        )

            rec_stack.discard(name)

        for ext in self.list():
            if ext.name not in visited:
                visit(ext.name, [])

    def init_all(
        self, app, enabled: Optional[List[str]] = None, skip_missing: bool = False
    ) -> None:
        """
        Initialize all or selected extensions.

        Args:
            app: Flask application
            enabled: List of extension names to enable (None = all)
            skip_missing: If True, skip disabled extensions without error

        Raises:
            ExtensionDependencyError: If dependencies not satisfied
            ExtensionInitError: If initialization fails
        """
        # Detect circular dependencies
        self._detect_circular_dependencies()

        # Determine which extensions to initialize
        if enabled is None:
            to_initialize = [e.name for e in self.list()]
        else:
            to_initialize = enabled

        # Validate all requested extensions
        for name in to_initialize:
            if name not in self._instances:
                if skip_missing:
                    continue
                raise ExtensionNotFoundError(f"Extension '{name}' not found")

            self._check_dependencies(name, to_initialize)

        # Initialize in priority order
        for ext in self.list(sorted_by_priority=True):
            if ext.name not in to_initialize:
                continue

            if ext.name in self._initialized:
                continue

            try:
                ext.init_app(app)
                self._initialized.add(ext.name)
            except Exception as e:
                raise ExtensionInitError(
                    f"Failed to initialize extension '{ext.name}': {str(e)}"
                ) from e

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
        ext = self.get(name)
        if not ext:
            raise ExtensionNotFoundError(f"Extension '{name}' not found")

        try:
            ext.init_app(app)
            self._initialized.add(name)
        except Exception as e:
            raise ExtensionInitError(f"Failed to initialize '{name}': {str(e)}") from e

    def is_initialized(self, name: str) -> bool:
        """
        Check if an extension is initialized.

        Args:
            name: Extension name

        Returns:
            bool: True if initialized
        """
        return name in self._initialized

    def shutdown(self, app=None) -> None:
        """
        Shutdown all extensions in reverse order.

        Args:
            app: Flask application (optional)
        """
        for ext in reversed(self.list()):
            if hasattr(ext, "shutdown"):
                try:
                    ext.shutdown(app)
                except Exception as e:
                    # Log but don't raise during shutdown
                    import warnings

                    warnings.warn(f"Error shutting down {ext.name}: {e}")

        self._initialized.clear()
