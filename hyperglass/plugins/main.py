"""Register all plugins."""

# Standard Library
from inspect import isclass

# Local
from . import _builtin
from ._output import OutputPlugin
from ._register import register_output_plugin


def init_plugins() -> None:
    """Initialize all plugins."""
    for name in dir(_builtin):
        plugin = getattr(_builtin, name)
        if isclass(plugin):
            if issubclass(plugin, OutputPlugin):
                register_output_plugin(plugin)
