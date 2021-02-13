"""Test Arista JSON Parsing."""

# Standard Library
import sys
import json
from pathlib import Path

# Project
from hyperglass.log import log

# Local
from .arista import parse_arista

SAMPLE_FILE = Path(__file__).parent.parent / "models" / "parsing" / "arista_route.json"

if __name__ == "__main__":
    if len(sys.argv) == 2:
        sample = sys.argv[1]
    else:
        with SAMPLE_FILE.open("r") as file:
            sample = file.read()

    parsed = parse_arista([sample])
    log.info(json.dumps(parsed, indent=2))
    sys.exit(0)
