"""hyperglass Plugins."""

# Local
from .main import register_plugin, init_builtin_plugins
from ._input import InputPlugin, InputPluginValidationReturn
from ._output import OutputType, OutputPlugin
from ._manager import InputPluginManager, OutputPluginManager

__all__ = (
    "init_builtin_plugins",
    "InputPlugin",
    "InputPluginManager",
    "InputPluginValidationReturn",
    "OutputPlugin",
    "OutputPluginManager",
    "OutputType",
    "register_plugin",
)
