"""Remove anything before the command if found in output."""

# Project
from hyperglass.models.config.devices import Device

# Local
from .._output import OutputPlugin


class RemoveCommand(OutputPlugin):
    """Remove anything before the command if found in output."""

    def process(self, device_output: str, device: Device) -> str:
        """Remove anything before the command if found in output."""
        output = device_output.strip().split("\n")

        for command in device.directive_commands:
            for line in output:
                if command in line:
                    idx = output.index(line) + 1
                    output = output[idx:]

        return "\n".join(output)
