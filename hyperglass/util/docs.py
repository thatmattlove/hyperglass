"""Helpers for hyperglass docs."""

# Standard Library
import json
from pathlib import Path


def create_platform_list() -> str:
    """Create a list of platforms as a typescript file for use by the docs."""
    # Third Party
    from netmiko.ssh_dispatcher import CLASS_MAPPER  # type: ignore

    project_root = Path(__file__).parent.parent.parent

    dir_ = project_root / "docs"
    file_ = dir_ / "platforms.json"

    builtin_directives = project_root / "hyperglass" / "defaults" / "directives"

    names = [f.stem for f in builtin_directives.iterdir() if not f.name.startswith("_")]

    platforms = [[p, p in names] for p in CLASS_MAPPER.keys()]

    with file_.open("w+") as opened_file:
        json.dump(platforms, opened_file)

    return f"Wrote platforms to {file_!s}"
