"""Test Juniper XML Parsing."""

# Standard Library
import sys
import json
from pathlib import Path

# Project
from hyperglass.log import log

# Local
from .juniper import parse_juniper

SAMPLE_FILES = (
    Path(__file__).parent.parent / "models" / "parsing" / "juniper_route_direct.xml",
    Path(__file__).parent.parent / "models" / "parsing" / "juniper_route_indirect.xml",
    Path(__file__).parent.parent / "models" / "parsing" / "juniper_route_aspath.xml",
)


@log.catch
def run():
    """Run tests."""
    samples = ()
    if len(sys.argv) == 2:
        samples += (sys.argv[1],)
    else:
        for sample_file in SAMPLE_FILES:
            with sample_file.open("r") as file:
                samples += (file.read(),)

    for sample in samples:
        parsed = parse_juniper([sample])
        log.info(json.dumps(parsed, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    run()
