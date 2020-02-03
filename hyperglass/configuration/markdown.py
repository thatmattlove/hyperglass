"""Markdown processing utility functions."""

# Third Party
from aiofile import AIOFile

# Project
from hyperglass.util import log


async def _get_file(path_obj):
    """Read a file.

    Arguments:
        path_obj {Path} -- Path to file.

    Returns:
        {str} -- File contents
    """
    async with AIOFile(path_obj, "r") as raw_file:
        file = await raw_file.read()
        return file


async def format_markdown(content, params):
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


async def get_markdown(config_path, default, params):
    """Get markdown file if specified, or use default.

    Format the content with config parameters.

    Arguments:
        config_path {object} -- content config
        default {str} -- default content

    Returns:
        {str} -- Formatted content
    """
    log.debug(f"Getting Markdown content for '{params['title']}'")

    if config_path.enable and config_path.file is not None:
        md = await _get_file(config_path.file)
    else:
        md = default

    log.debug(f"Unformatted Content for '{params['title']}':\n{md}")

    md_fmt = await format_markdown(md, params)

    log.debug(f"Formatted Content for '{params['title']}':\n{md_fmt}")

    return md_fmt
