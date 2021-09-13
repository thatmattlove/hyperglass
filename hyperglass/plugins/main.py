"""Register all plugins."""

# Standard Library
import sys
from typing import Any, Tuple
from inspect import isclass, getmembers
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location

# Project
from hyperglass.log import log

# Local
from . import _builtin
from ._input import InputPlugin
from ._output import OutputPlugin
from ._manager import InputPluginManager, OutputPluginManager

_PLUGIN_GLOBALS = {"InputPlugin": InputPlugin, "OutputPlugin": OutputPlugin, "log": log}


def _is_class(module: Any, obj: object) -> bool:
    if isclass(obj):
        # Get the object's containing module name.
        obj_module_name: str = getattr(obj, "__module__", "")
        # Get the module's name.
        module_name: str = getattr(module, "__name__", None)
        # Only validate objects that are members of the module.
        return module_name in obj_module_name
    return False


def _register_from_module(module: Any, **kwargs: Any) -> Tuple[str, ...]:
    """Register defined classes from the module."""
    failures = ()
    defs = getmembers(module, lambda o: _is_class(module, o))
    for name, plugin in defs:
        if issubclass(plugin, OutputPlugin):
            manager = OutputPluginManager()
        elif issubclass(plugin, InputPlugin):
            manager = InputPluginManager()
        else:
            failures += (name,)
            continue
        manager.register(plugin, **kwargs)
        return failures
    return failures


def _module_from_file(file: Path) -> Any:
    """Import a plugin module from its file Path object."""
    name = file.name.split(".")[0]
    spec = spec_from_file_location(f"hyperglass.plugins.external.{name}", file)
    module = module_from_spec(spec)
    for k, v in _PLUGIN_GLOBALS.items():
        setattr(module, k, v)
    spec.loader.exec_module(module)
    sys.modules[module.__name__] = module
    return module


def init_builtin_plugins() -> None:
    """Initialize all built-in plugins."""
    _register_from_module(_builtin)


def register_plugin(plugin_file: Path, **kwargs) -> Tuple[str, ...]:
    """Register an external plugin by file path."""
    if plugin_file.exists():
        module = _module_from_file(plugin_file)
        results = _register_from_module(module, **kwargs)
        return results
    raise FileNotFoundError(str(plugin_file))
