import importlib
import logging

from pathlib import Path
from typing import Callable

from dlo.adapters.adapter import Adapter
from dlo.common.exception import errors

log = logging.getLogger("__name__")


def import_module(name: str):
    """Imports a module given a name."""
    return importlib.import_module(name)  # type: ignore


# TODO: Add Namespace capabity in the future
class ToolRegistry:
    tools: dict[str, Callable[..., Adapter]] = {}

    @classmethod
    def register(cls, name: str, creater_fn: Adapter) -> None:
        """Register new tool"""
        cls.tools[name] = creater_fn
        log.info

    @classmethod
    def unregister(cls, name: str) -> None:
        """Unregister a tool"""
        cls.tools.pop(name, None)

    @classmethod
    def get(cls, name: str) -> Adapter:
        """Create a Tools type"""
        try:
            func = cls.tools[name]
        except KeyError:
            raise errors.MethodNotFoundError(f"unknown tools type {name!r}")
        return func

    @classmethod
    def discover_and_register(cls, package_path: str):
        """Auto-discover all modules inside a given package path."""
        import pkgutil

        try:
            package = importlib.import_module(package_path)
            for module in pkgutil.iter_modules(package.__path__):
                module_path = f"{package_path}.{module.name}"
                import_module(module_path)
                log.info(f"Tools Loaded from package `{module_path}`")
        except ImportError:
            log.warning(f"Could not scan package '{package_path}'.")

    @classmethod
    def discover_and_register_from_dir(cls, package_path: str | Path):
        package_dir = Path(package_path)

        try:
            for file in package_dir.glob("*.py"):
                if file.name == "__init__.py":
                    continue
                module_name = file.stem
                spec = importlib.util.spec_from_file_location(module_name, file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                log.info(f"Tools Loaded from file `{file}`")
        except Exception:
            log.warning(f"Could not scan directory '{package_dir}'.")


ToolRegistry.discover_and_register("dlo.agents.tools")
