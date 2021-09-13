"""hyperglass Plugins."""

# Local
from .main import init_plugins, register_plugin
from ._input import InputPlugin, InputPluginReturn
from ._output import OutputType, OutputPlugin
from ._manager import InputPluginManager, OutputPluginManager

__all__ = (
    "init_plugins",
    "InputPlugin",
    "InputPluginManager",
    "InputPluginReturn",
    "OutputPlugin",
    "OutputPluginManager",
    "OutputType",
    "register_plugin",
)
