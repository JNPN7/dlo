import importlib
import logging

from typing import Callable

from dlo.adapters.adapter import Adapter

log = logging.getLogger("__name__")


class ModuleInterface:
    """Represents a plugin interface. A plugin has a single register function."""

    @staticmethod
    def register() -> None:
        """Register the necessary items in the environment factory."""


def import_module(name: str) -> ModuleInterface:
    """Imports a module given a name."""
    return importlib.import_module(name)  # type: ignore


DEFAULT_PLUGINS = [
    "dlo.adapters.adapters.databricks",
]


class AdapterFactory:
    adapters: dict[str, Callable[..., Adapter]] = {}

    # LOADER
    def __init__(self, plugins: list[dict] = None):
        if plugins is None:
            plugins = []

        plugins.extend(DEFAULT_PLUGINS)

        for _plugin in plugins:
            try:
                plugin = import_module(_plugin)
                plugin.register(self)
            except ImportError:
                log.warning(f"Could not load plugin '{_plugin}' due to missing dependencies. This adapter will not be available.")  # noqa: E501
                pass

    @classmethod
    def register(cls, name: str, creater_fn: Adapter) -> None:
        """Register new adapter"""
        cls.adapters[name] = creater_fn

    @classmethod
    def unregister(cls, name: str) -> None:
        """Unregister a adapter"""
        cls.adapters.pop(name, None)

    @classmethod
    def create(cls, arguments: dict[str, any]) -> Adapter:
        """Create a execution engine type"""
        args_copy = arguments.copy()
        env_type = args_copy.pop("type")
        try:
            env_func = cls.execution_engine_funcs[env_type]
        except KeyError:
            raise ValueError(f"unknown adapter type {env_type!r}") from None
        return env_func(**args_copy)
