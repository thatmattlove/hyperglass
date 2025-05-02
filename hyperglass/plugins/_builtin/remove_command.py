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
    from hyperglass.models.api.query import Query


class RemoveCommand(OutputPlugin):
    """Remove anything before the command if found in output."""

    _hyperglass_builtin: bool = PrivateAttr(True)

    def process(self, *, output: OutputType, query: "Query") -> Sequence[str]:
        """Remove anything before the command if found in output."""

        def _remove_command(output_in: str) -> str:
            output_out = output_in.strip().split("\n")

            for command in query.device.directive_commands:
                for line in output_out:
                    if command in line:
                        idx = output_out.index(line) + 1
                        output_out = output_out[idx:]

            return "\n".join(output_out)

        if is_series(output):
            return tuple(_remove_command(o) for o in output)

        return output
