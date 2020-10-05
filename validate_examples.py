"""Validate example files."""

# Standard Library
import re
import sys
from pathlib import Path

# Third Party
import yaml

# Project
from hyperglass.util import set_app_path

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
                commented = re.compile(r"^(#\s*#?\s?).*$")
                if re.match(commented, line):
                    output.append(re.sub(r"^#\s*#?\s?$", "", line))
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
                if not re.match(r"^(#\s*#?\s?).*$|(^\-{3})", line):
                    output.append("# " + line)
                else:
                    output.append(line)
        with file.open("w") as f:
            f.write("".join(output))
    return True


def _validate_devices():
    # Project
    from hyperglass.configuration.models.devices import Devices

    with DEVICES.open() as raw:
        devices_dict = yaml.safe_load(raw.read()) or {}
    try:
        Devices(devices_dict.get("routers", []))
    except Exception as e:
        raise ValueError(str(e))
    return True


def _validate_commands():
    # Project
    from hyperglass.models.commands import Commands

    with COMMANDS.open() as raw:
        commands_dict = yaml.safe_load(raw.read()) or {}
    try:
        Commands.import_params(**commands_dict)
    except Exception as e:
        raise ValueError(str(e))
    return True


def _validate_main():
    # Project
    from hyperglass.configuration.models.params import Params

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
    set_app_path(required=True)
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
