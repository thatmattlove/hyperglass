"""Device output plugins."""

# Standard Library
from typing import TYPE_CHECKING, Union, Sequence

# Local
from ._base import DirectivePlugin

if TYPE_CHECKING:
    # Project
    from hyperglass.models.config.devices import Device
    from hyperglass.models.parsing.serialized import ParsedRoutes

OutputPluginReturn = Union[None, "ParsedRoutes", str]


class OutputPlugin(DirectivePlugin):
    """Plugin to interact with device command output."""

    directive_ids: Sequence[str] = ()

    def process(self, output: Union["ParsedRoutes", str], device: "Device") -> OutputPluginReturn:
        """Process or manipulate output from a device."""
        return None
