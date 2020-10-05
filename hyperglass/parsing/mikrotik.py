"""Mikrotik Output Parsing Functions."""

# Standard Library
import re

END_COLUMNS = ("DISTANCE", "STATUS")


def parse_mikrotik(output: str):
    """Parse Mikrotik output to remove garbage."""
    if output.split()[-1] in END_COLUMNS:
        # Mikrotik shows the columns with no rows if there is no data.
        # Rather than send back an empty table, send back an empty
        # response which is handled with a warning message.
        output = ""
    else:
        remove_lines = ()
        all_lines = output.splitlines()
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
        lines = [l for i, l in enumerate(lines) if i not in remove_lines]
        output = "\n".join(lines)

    return output
