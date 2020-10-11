"""Command parsers applied to all unstructured output."""


def remove_command(commands: str, output: str) -> str:
    """Remove anything before the command if found in output."""
    _output = output.strip().split("\n")

    for command in commands:
        for line in _output:
            if command in line:
                idx = _output.index(line) + 1
                _output = _output[idx:]

    return "\n".join(_output)


parsers = (remove_command,)
