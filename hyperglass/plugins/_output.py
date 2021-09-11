"""Device output plugins."""

# Standard Library
from abc import abstractmethod

# Project
from hyperglass.models.config.devices import Device

# Local
from ._base import HyperglassPlugin


class OutputPlugin(HyperglassPlugin):
    """Plugin to interact with device command output."""

    @abstractmethod
    def process(self, device_output: str, device: Device) -> str:
        """Process/manipulate output from a device."""
        pass
