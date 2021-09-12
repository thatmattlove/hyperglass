"""Device output plugins."""

# Standard Library
from typing import TYPE_CHECKING, Union

# Local
from ._base import HyperglassPlugin

if TYPE_CHECKING:
    # Project
    from hyperglass.models.config.devices import Device
    from hyperglass.models.parsing.serialized import ParsedRoutes

OutputPluginReturn = Union[None, "ParsedRoutes", str]


class OutputPlugin(HyperglassPlugin):
    """Plugin to interact with device command output."""

    def process(self, output: Union["ParsedRoutes", str], device: "Device") -> OutputPluginReturn:
        """Process or manipulate output from a device."""
        return None
