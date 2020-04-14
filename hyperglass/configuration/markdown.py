"""Markdown processing utility functions."""

# Project
from hyperglass.log import log


def _get_file(path_obj):
    """Read a file.

    Arguments:
        path_obj {Path} -- Path to file.

    Returns:
        {str} -- File contents
    """
    with path_obj.open("r") as raw_file:
        return raw_file.read()


def format_markdown(content, params):
    """Format content with config parameters.

    Arguments:
        content {str} -- Unformatted content

    Returns:
        {str} -- Formatted content
    """
    try:
        fmt = content.format(**params)
    except KeyError:
        fmt = content
    return fmt


def get_markdown(config_path, default, params):
    """Get markdown file if specified, or use default.

    Format the content with config parameters.

    Arguments:
        config_path {object} -- content config
        default {str} -- default content

    Returns:
        {str} -- Formatted content
    """
    log.trace(f"Getting Markdown content for '{params['title']}'")

    if config_path.enable and config_path.file is not None:
        md = _get_file(config_path.file)
    else:
        md = default

    log.trace(f"Unformatted Content for '{params['title']}':\n{md}")

    md_fmt = format_markdown(md, params)

    log.trace(f"Formatted Content for '{params['title']}':\n{md_fmt}")

    return md_fmt
