"""Register all plugins."""

# Standard Library
from inspect import isclass

# Local
from . import _builtin
from ._input import InputPlugin
from ._output import OutputPlugin
from ._manager import InputPluginManager, OutputPluginManager


def init_plugins() -> None:
    """Initialize all plugins."""
    for name in dir(_builtin):
        plugin = getattr(_builtin, name)
        if isclass(plugin):
            if issubclass(plugin, OutputPlugin):
                manager = OutputPluginManager()
            elif issubclass(plugin, InputPlugin):
                manager = InputPluginManager()
            else:
                continue
            manager.register(plugin)
