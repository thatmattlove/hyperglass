"""Remove anything before the command if found in output."""

# Standard Library
from typing import TYPE_CHECKING

# Third Party
from pydantic import PrivateAttr

# Local
from .._output import OutputPlugin

if TYPE_CHECKING:
    # Project
    from hyperglass.models.config.devices import Device


class RemoveCommand(OutputPlugin):
    """Remove anything before the command if found in output."""

    __hyperglass_builtin__: bool = PrivateAttr(True)

    def process(self, device_output: str, device: "Device") -> str:
        """Remove anything before the command if found in output."""
        output = device_output.strip().split("\n")

        for command in device.directive_commands:
            for line in output:
                if command in line:
                    idx = output.index(line) + 1
                    output = output[idx:]

        return "\n".join(output)
