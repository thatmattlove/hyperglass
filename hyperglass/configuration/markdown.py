"""Markdown processing utility functions."""

# Standard Library
import typing as t
from pathlib import Path

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models import HyperglassModel


def get_markdown(config: "HyperglassModel", default: str, params: t.Dict[str, t.Any]) -> str:
    """Get markdown file if specified, or use default."""

    if config.enable and config.file is not None:
        # with config_path.file
        if hasattr(config, "file") and isinstance(config.file, Path):
            with config.file.open("r") as config_file:
                md = config_file.read()
    else:
        md = default

    try:
        return md.format(**params)
    except KeyError:
        return md
