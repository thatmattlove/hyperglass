"""Remove anything before the command if found in output."""

# Standard Library
from typing import TYPE_CHECKING, Sequence

# Third Party
from pydantic import PrivateAttr

# Project
from hyperglass.util.typing import is_series

# Local
from .._output import OutputType, OutputPlugin

if TYPE_CHECKING:
    # Project
    from hyperglass.models.config.devices import Device


class RemoveCommand(OutputPlugin):
    """Remove anything before the command if found in output."""

    __hyperglass_builtin__: bool = PrivateAttr(True)

    def process(self, device_output: OutputType, device: "Device") -> Sequence[str]:
        """Remove anything before the command if found in output."""

        def _remove_command(output_in: str) -> str:
            output_out = device_output.strip().split("\n")

            for command in device.directive_commands:
                for line in output_out:
                    if command in line:
                        idx = output_out.index(line) + 1
                        output_out = output_out[idx:]

            return "\n".join(output_out)

        if is_series(device_output):
            return tuple(_remove_command(o) for o in device_output)

        return device_output
