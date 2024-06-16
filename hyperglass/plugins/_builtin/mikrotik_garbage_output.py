"""Remove anything before the command if found in output."""

# Standard Library
import re
import typing as t

# Third Party
from pydantic import PrivateAttr

# Project
from hyperglass.types import Series

# Local
from .._output import OutputType, OutputPlugin

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.api.query import Query


class MikrotikGarbageOutput(OutputPlugin):
    """Parse Mikrotik output to remove garbage."""

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: t.Sequence[str] = ("mikrotik_routeros", "mikrotik_switchos")
    directives: t.Sequence[str] = (
        "__hyperglass_mikrotik_bgp_aspath__",
        "__hyperglass_mikrotik_bgp_community__",
        "__hyperglass_mikrotik_bgp_route__",
        "__hyperglass_mikrotik_ping__",
        "__hyperglass_mikrotik_traceroute__",
    )

    def process(self, *, output: OutputType, query: "Query") -> Series[str]:
        """Parse Mikrotik output to remove garbage."""

        result = ()

        for each_output in output:
            if len(each_output) != 0:
                if each_output.split()[-1] in ("DISTANCE", "STATUS"):
                    # Mikrotik shows the columns with no rows if there is no data.
                    # Rather than send back an empty table, send back an empty
                    # response which is handled with a warning message.
                    each_output = ""
                else:
                    remove_lines = ()
                    all_lines = each_output.splitlines()
                    # Starting index for rows (after the column row).
                    start = 1
                    # Extract the column row.
                    column_line = " ".join(all_lines[0].split())

                    for i, line in enumerate(all_lines[1:]):
                        # Remove all the newline characters (which differ line to
                        # line) for comparison purposes.
                        normalized = " ".join(line.split())

                        # Remove ansii characters that aren't caught by Netmiko.
                        normalized = re.sub(r"\\x1b\[\S{2}\s", "", normalized)

                        if column_line in normalized:
                            # Mikrotik often re-inserts the column row in the output,
                            # effectively 'starting over'. In that case, re-assign
                            # the column row and starting index to that point.
                            column_line = re.sub(r"\[\S{2}\s", "", line)
                            start = i + 2

                        if "[Q quit|D dump|C-z pause]" in normalized:
                            # Remove Mikrotik's unhelpful helpers from the output.
                            remove_lines += (i + 1,)

                    # Combine the column row and the data rows from the starting
                    # index onward.
                    lines = [column_line, *all_lines[start:]]

                    # Remove any lines marked for removal and re-join with a single
                    # newline character.
                    lines = [line for idx, line in enumerate(lines) if idx not in remove_lines]
                    result += ("\n".join(lines),)

        return result
