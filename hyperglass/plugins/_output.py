"""Device output plugins."""

# Standard Library
from typing import TYPE_CHECKING, Union

# Project
from hyperglass.log import log
from hyperglass.types import Series

# Local
from ._base import DirectivePlugin, DeviceTypePlugin, HyperglassPlugin

if TYPE_CHECKING:
    # Project
    from hyperglass.models.data import OutputDataModel
    from hyperglass.models.config.devices import Device

OutputType = Union["OutputDataModel", Series[str]]


class OutputPlugin(HyperglassPlugin, DirectivePlugin, DeviceTypePlugin):
    """Plugin to interact with device command output."""

    def process(self, output: OutputType, device: "Device") -> OutputType:
        """Process or manipulate output from a device."""
        log.warning("Output plugin '{}' has not implemented a 'process()' method", self.name)
        return output
