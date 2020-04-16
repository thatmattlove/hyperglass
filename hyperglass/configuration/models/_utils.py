"""Utility Functions for Pydantic Models."""

# Standard Library
import os
from pathlib import Path

# Project
from hyperglass.log import log


def validate_image(value):
    """Convert file path to URL path.

    Arguments:
        value {FilePath} -- Path to logo file.

    Returns:
        {str} -- Formatted logo path
    """
    config_path = Path(os.environ["hyperglass_directory"])
    base_path = [v for v in value.split("/") if v != ""]

    if base_path[0] not in ("images", "custom"):
        raise ValueError(
            f"Logo files must be in the 'custom/' directory of your hyperglass directory. Got: {value}"
        )

    if base_path[0] == "custom":
        file = config_path / "static" / "custom" / "/".join(base_path[1:])

    else:
        file = config_path / "static" / "images" / "/".join(base_path[1:])

    log.error(file)
    if not file.exists():
        raise ValueError(f"'{str(file)}' does not exist")

    base_index = file.parts.index(base_path[0])

    return "/".join(file.parts[base_index:])
