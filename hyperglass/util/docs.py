"""Helpers for hyperglass docs."""

# Standard Library
import json
import typing as t
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location


class PlatformSpec(t.TypedDict):
    """Definition for each platform."""

    name: str
    keys: t.Tuple[str, ...]
    native: bool


def get_directive_variable(path: Path, variable: str) -> t.Any:
    """Read a variable from a directive file."""

    name, _ = path.name.split(".")
    spec = spec_from_file_location(name, location=path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    exports = tuple(getattr(module, e, None) for e in dir(module) if e == variable)
    if len(exports) < 1:
        raise RuntimeError(f"'{path!s} exists', but it is missing a variable named '{variable}'")

    value, *_ = exports
    return value


def create_platform_list() -> str:
    """Create a list of platforms as a JSON file for use by the docs."""
    # Third Party
    from netmiko.ssh_dispatcher import CLASS_MAPPER  # type: ignore

    project_root = Path(__file__).parent.parent.parent

    dir_ = project_root / "docs"
    file_ = dir_ / "platforms.json"

    builtin_directives = project_root / "hyperglass" / "defaults" / "directives"

    platforms: t.Tuple[PlatformSpec] = ()

    keys = []

    for path in builtin_directives.iterdir():
        if not path.name.startswith("_"):
            name = get_directive_variable(path, "NAME")
            if not isinstance(name, str):
                raise RuntimeError("'NAME' variable is missing or invalid in '{!s}'".format(path))
            _platforms = get_directive_variable(path, "PLATFORMS")
            if not isinstance(_platforms, t.Tuple, t.List):
                raise RuntimeError(
                    "'PLATFORMS' variable is missing or invalid in '{!s}'".format(path)
                )
            spec: PlatformSpec = {"name": name, "keys": _platforms, "native": True}
            platforms += (spec,)
            keys = [*keys, *_platforms]

    for key in CLASS_MAPPER.keys():
        if key not in keys:
            spec: PlatformSpec = {"name": "", "keys": (key,), "native": False}
            platforms += (spec,)

    sorted_platforms = list(platforms)
    sorted_platforms.sort(key=lambda x: x["keys"][0])
    sorted_platforms.sort(key=lambda x: not x["native"])

    with file_.open("w+") as opened_file:
        json.dump(sorted_platforms, opened_file)

    return f"Wrote platforms to {file_!s}"
