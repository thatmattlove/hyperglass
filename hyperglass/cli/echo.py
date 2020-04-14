"""Helper functions for CLI message printing."""
# Standard Library
import re

# Third Party
from click import echo, style

# Project
from hyperglass.cli.static import CMD_HELP, Message
from hyperglass.cli.exceptions import CliError


def cmd_help(emoji="", help_text="", supports_color=False):
    """Print formatted command help."""
    if supports_color:
        help_str = emoji + style(help_text, **CMD_HELP)
    else:
        help_str = help_text
    return help_str


def _base_formatter(_text, _state, _callback, *args, **kwargs):
    """Format text block, replace template strings with keyword arguments.

    Arguments:
        state {dict} -- Text format attributes
        label {dict} -- Keyword format attributes
        text {[type]} -- Text to format
        callback {function} -- Callback function

    Returns:
        {str|ClickException} -- Formatted output
    """
    fmt = Message(_state)

    if _callback is None:
        _callback = style

    nargs = ()
    for i in args:
        if not isinstance(i, str):
            nargs += (str(i),)
        else:
            nargs += (i,)

    for k, v in kwargs.items():
        if not isinstance(v, str):
            v = str(v)
        kwargs[k] = style(v, **fmt.kw)

    text_all = re.split(r"(\{\w+\})", _text)
    text_all = [style(i, **fmt.msg) for i in text_all]
    text_all = [i.format(*nargs, **kwargs) for i in text_all]

    if fmt.emoji:
        text_all.insert(0, fmt.emoji)

    text_fmt = "".join(text_all)

    return _callback(text_fmt)


def info(text, *args, **kwargs):
    """Generate formatted informational text.

    Arguments:
        text {str} -- Text to format
        callback {callable} -- Callback function (default: {echo})

    Returns:
        {str} -- Informational output
    """
    return _base_formatter(_state="info", _text=text, _callback=echo, *args, **kwargs)


def error(text, *args, **kwargs):
    """Generate formatted exception.

    Arguments:
        text {str} -- Text to format
        callback {callable} -- Callback function (default: {echo})

    Raises:
        ClickException: Raised after formatting
    """
    raise _base_formatter(text, "error", CliError, *args, **kwargs)


def success(text, *args, **kwargs):
    """Generate formatted success text.

    Arguments:
        text {str} -- Text to format
        callback {callable} -- Callback function (default: {echo})

    Returns:
        {str} -- Success output
    """
    return _base_formatter(
        _state="success", _text=text, _callback=echo, *args, **kwargs
    )


def warning(text, *args, **kwargs):
    """Generate formatted warning text.

    Arguments:
        text {str} -- Text to format
        callback {callable} -- Callback function (default: {echo})

    Returns:
        {str} -- Warning output
    """
    return _base_formatter(
        _state="warning", _text=text, _callback=echo, *args, **kwargs
    )


def label(text, *args, **kwargs):
    """Generate formatted info text with accented labels.

    Arguments:
        text {str} -- Text to format
        callback {callable} -- Callback function (default: {echo})

    Returns:
        {str} -- Label output
    """
    return _base_formatter(_state="label", _text=text, _callback=echo, *args, **kwargs)


def status(text, *args, **kwargs):
    """Generate formatted status text.

    Arguments:
        text {str} -- Text to format
        callback {callable} -- Callback function (default: {echo})

    Returns:
        {str} -- Status output
    """
    return _base_formatter(_state="status", _text=text, _callback=echo, *args, **kwargs)
