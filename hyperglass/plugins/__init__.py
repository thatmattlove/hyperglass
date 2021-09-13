"""hyperglass Plugins."""

# Local
from .main import register_plugin, init_builtin_plugins
from ._input import InputPlugin, InputPluginReturn
from ._output import OutputType, OutputPlugin
from ._manager import InputPluginManager, OutputPluginManager

__all__ = (
    "init_builtin_plugins",
    "InputPlugin",
    "InputPluginManager",
    "InputPluginReturn",
    "OutputPlugin",
    "OutputPluginManager",
    "OutputType",
    "register_plugin",
)
