"""Validate example files."""
# Standard Library
import re
import sys
from pathlib import Path

# Third Party
import yaml

# Project
from hyperglass.util import set_app_path
from hyperglass.configuration.models.params import Params
from hyperglass.configuration.models.routers import Routers
from hyperglass.configuration.models.commands import Commands

EXAMPLES = Path(__file__).parent.parent / "hyperglass" / "examples"

DEVICES = EXAMPLES / "devices.yaml"
COMMANDS = EXAMPLES / "commands.yaml"
MAIN = EXAMPLES / "hyperglass.yaml"


def _uncomment_files():
    """Uncomment out files."""
    for file in (MAIN, COMMANDS):
        output = []
        with file.open("r") as f:
            for line in f.readlines():
                if re.match(r"^(#\s+[a-z0-9]+)|(#\s+\-\s.*$)", line):
                    output.append(re.sub(r"^(#\s)", "", line))
                else:
                    output.append(line)
        with file.open("w") as f:
            f.write("".join(output))
    return True


def _comment_optional_files():
    """Comment out files."""
    for file in (MAIN, COMMANDS):
        output = []
        with file.open("r") as f:
            for line in f.readlines():
                if not re.match(r"^(#\s+[A-Za-z0-9])|(^\-{3})", line):
                    output.append("# " + line)
                else:
                    output.append(line)
        with file.open("w") as f:
            f.write("".join(output))
    return True


def _validate_devices():
    with DEVICES.open() as raw:
        devices_dict = yaml.safe_load(raw.read()) or {}
    try:
        Routers._import(devices_dict.get("routers", []))
    except Exception as e:
        raise ValueError(str(e))
    return True


def _validate_commands():
    with COMMANDS.open() as raw:
        commands_dict = yaml.safe_load(raw.read()) or {}
    try:
        Commands.import_params(commands_dict)
    except Exception as e:
        raise ValueError(str(e))
    return True


def _validate_main():
    with MAIN.open() as raw:
        main_dict = yaml.safe_load(raw.read()) or {}
    try:
        Params(**main_dict)
    except Exception as e:
        raise
        raise ValueError(str(e))
    return True


def validate_all():
    """Validate all example configs against configuration models."""
    _uncomment_files()
    for validator in (_validate_main, _validate_commands, _validate_devices):
        try:
            validator()
        except ValueError as e:
            raise RuntimeError(str(e))
    return True


if __name__ == "__main__":
    set_app_path()
    try:
        all_passed = validate_all()
        message = "All tests passed"
        status = 0
    except RuntimeError as e:
        message = str(e)
        status = 1
    if status == 0:
        _comment_optional_files()
    print(message)
    sys.exit(status)
