"""Device output plugins."""

# Standard Library
import abc

# Project
from hyperglass.models import HyperglassModel
from hyperglass.models.config.devices import Device


class OutputPlugin(HyperglassModel, abc.ABC):
    """Plugin to interact with device command output."""

    def __eq__(self, other: "OutputPlugin"):
        """Other plugin is equal to this plugin."""
        return other and self.__repr_name__ == other.__repr_name__

    def __ne__(self, other: "OutputPlugin"):
        """Other plugin is not equal to this plugin."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Create a hashed representation of this plugin's name."""
        return hash(self.__repr_name__)

    @abc.abstractmethod
    def process(self, device_output: str, device: Device) -> str:
        """Process/manipulate output from a device."""
        pass
