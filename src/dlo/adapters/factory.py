import importlib
import logging

from typing import Callable

from dlo.adapters.adapter import Adapter
from dlo.common.exceptions import errors

log = logging.getLogger("__name__")

ADAPTERS_PLUGIN_DIRS = ["dlo.adapters.adapters"]


class ModuleInterface:
    """Represents a plugin interface. A plugin has a single register function."""

    @staticmethod
    def register() -> None:
        """Register the necessary items in the environment factory."""


def import_module(name: str) -> ModuleInterface:
    """Imports a module given a name."""
    return importlib.import_module(name)  # type: ignore


class AdapterFactory:
    adapters: dict[str, Callable[..., Adapter]] = {}
    _plugin_registry: dict[str, str] = {}  # name -> module path (not yet imported)

    # LOADER
    def __init__(self, plugins: list[str] = None, plugin_packages: list[str] = None):
        plugins = list(plugins or [])

        # Auto-discover from packages
        for pkg in plugin_packages or ADAPTERS_PLUGIN_DIRS:
            self._discover_and_register(pkg)

        for plugin_path in plugins:
            self._register_plugin_path(plugin_path)

    def _discover_and_register(self, package_path: str) -> list[str]:
        """Auto-discover all modules inside a given package path."""
        import pkgutil

        try:
            package = importlib.import_module(package_path)
            for module in pkgutil.iter_modules(package.__path__):
                module_path = f"{package_path}.{module.name}"
                self._register_plugin_path(module_path)
        except ImportError:
            log.warning(f"Could not scan package '{package_path}'.")

    def _register_plugin_path(self, plugin: str):
        """Manually register a plugin path without importing it."""
        name = plugin.split(".")[-1]
        self._plugin_registry[name] = plugin

    @classmethod
    def register(cls, name: str, creater_fn: Adapter) -> None:
        """Register new adapter"""
        cls.adapters[name] = creater_fn

    @classmethod
    def unregister(cls, name: str) -> None:
        """Unregister a adapter"""
        cls.adapters.pop(name, None)

    @classmethod
    def _load_plugin(cls, name: str) -> None:
        """Lazily import and register a plugin only when needed."""
        if name in cls.adapters:
            return

        if name not in cls._plugin_registry:
            raise errors.MethodNotFoundError(f"unknown adapter type {name!r}")

        plugin_path = cls._plugin_registry[name]
        try:
            plugin = import_module(plugin_path)
            plugin.register(cls, name)
        except ImportError:
            raise errors.DloRuntimeError(
                f"Could not load plugin '{plugin_path}' due to missing dependencies."
            )

    @classmethod
    def create(cls, **args) -> Adapter:
        """Create a Adapter type"""
        args_copy = args.copy()
        env_type = args_copy.pop("type")

        cls._load_plugin(env_type)

        try:
            env_func = cls.adapters[env_type]
        except KeyError:
            raise errors.MethodNotFoundError(f"unknown adapter type {env_type!r}")
        return env_func(**args_copy)
