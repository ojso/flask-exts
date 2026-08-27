from abc import ABC
from typing import Dict, Optional, Type, List


class PluginBase(ABC):
    """
    Base class for all plugins.

    Subclasses are automatically registered in the registry.
    """

    name: str = ""
    namespace: str = ""
    version: str = "1.0.0"
    dependencies: List[str] = []

    _registry: Dict[str, Type["PluginBase"]] = {}

    def __init_subclass__(cls, **kwargs):
        """Auto-register subclass on definition."""
        super().__init_subclass__(**kwargs)
        if cls.name:
            key = f"{cls.namespace}.{cls.name}" if cls.namespace else cls.name
            PluginBase._registry[key] = cls

    @classmethod
    def get_registry(cls) -> Dict[str, Type["PluginBase"]]:
        """Get the complete plugin registry."""
        return PluginBase._registry

    @classmethod
    def get_plugin(cls, name: str) -> Optional[Type["PluginBase"]]:
        """Get a plugin class by its name."""
        return PluginBase._registry.get(name)

    @classmethod
    def list_plugins(cls) -> List[str]:
        """List all registered plugin names."""
        return list(PluginBase._registry.keys())
