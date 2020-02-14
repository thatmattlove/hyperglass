"""Help formatting.

https://github.com/click-contrib/click-help-colors
MIT License

Copyright (c) 2016 Roman Tonkonozhko

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Standard Library
import random

# Third Party
import click


def random_colors(*commands):
    """From tuple of commands, generate random but unique colors."""
    colors = ["blue", "green", "red", "yellow", "magenta", "cyan", "white"]
    num_colors = len(colors)
    num_commands = len(commands)

    if num_commands >= num_colors:
        colors += colors

    unique_colors = random.sample(colors, num_commands)
    commands_fmt = {}
    for i, cmd in enumerate(commands):
        commands_fmt.update({cmd: {"fg": unique_colors[i], "bold": True}})
    commands_fmt.update({"--help": {"fg": "white"}})
    return commands_fmt


class HelpColorsFormatter(click.HelpFormatter):
    """Click help formatting plugin. See file docstring for license.

    Modified from original copy to support click.style() instead of
    direct ANSII string formatting.
    """

    def __init__(
        self,
        headers_color=None,
        options_color=None,
        options_custom_colors=None,
        *args,
        **kwargs
    ):
        """Initialize help formatter.

        Keyword Arguments:
            headers_color {dict} -- click.style() paramters for header
            options_color {dict} -- click.style() paramters for options
            options_custom_colors {dict} -- click.style() paramters for options by name
        """
        self.headers_color = headers_color or {}
        self.options_color = options_color or {}
        self.options_custom_colors = options_custom_colors or {}

        super().__init__(indent_increment=3, *args, **kwargs)

    def _pick_color(self, option_name):
        """Filter options and pass relevant click.style() options for command."""
        opt = option_name.split()[0].strip(",")
        color = {}
        if self.options_custom_colors and opt in self.options_custom_colors.keys():
            color = self.options_custom_colors[opt]
        else:
            color = self.options_color
        return color

    def write_usage(self, prog, args="", prefix="Usage: "):
        """Write Usage: section."""
        prefix_fmt = click.style(prefix, **self.headers_color)
        super().write_usage(prog, args, prefix=prefix_fmt)

    def write_heading(self, heading):
        """Write Heading section."""
        heading_fmt = click.style(heading, **self.headers_color)
        super().write_heading(heading_fmt)

    def write_dl(self, rows, **kwargs):
        """Write Options section."""
        colorized_rows = [
            (click.style(row[0], **self._pick_color(row[0])), row[1]) for row in rows
        ]
        super().write_dl(colorized_rows, **kwargs)


class HelpColorsMixin:
    """Click help formatting plugin. See file docstring for license.

    Modified from original copy to support click.style() instead of
    direct ANSII string formatting.
    """

    def __init__(
        self,
        help_headers_color=None,
        help_options_color=None,
        help_options_custom_colors=None,
        *args,
        **kwargs
    ):
        """Initialize help mixin."""
        self.help_headers_color = help_headers_color or {}
        self.help_options_color = help_options_color or {}
        self.help_options_custom_colors = help_options_custom_colors or {}
        super().__init__(*args, **kwargs)

    def get_help(self, ctx):
        """Format help."""
        formatter = HelpColorsFormatter(
            width=ctx.terminal_width,
            max_width=ctx.max_content_width,
            headers_color=self.help_headers_color,
            options_color=self.help_options_color,
            options_custom_colors=self.help_options_custom_colors,
        )
        self.format_help(ctx, formatter)
        return formatter.getvalue().rstrip("\n")


class HelpColorsGroup(HelpColorsMixin, click.Group):
    """Click help formatting plugin. See file docstring for license.

    Modified from original copy to support click.style() instead of
    direct ANSII string formatting.
    """

    def __init__(self, *args, **kwargs):
        """Initialize group formatter."""
        super().__init__(*args, **kwargs)

    def command(self, *args, **kwargs):
        """Set command values."""
        kwargs.setdefault("cls", HelpColorsCommand)
        kwargs.setdefault("help_headers_color", self.help_headers_color)
        kwargs.setdefault("help_options_color", self.help_options_color)
        kwargs.setdefault("help_options_custom_colors", self.help_options_custom_colors)
        return super().command(*args, **kwargs)

    def group(self, *args, **kwargs):
        """Set group values."""
        kwargs.setdefault("cls", HelpColorsGroup)
        kwargs.setdefault("help_headers_color", self.help_headers_color)
        kwargs.setdefault("help_options_color", self.help_options_color)
        kwargs.setdefault("help_options_custom_colors", self.help_options_custom_colors)
        return super().group(*args, **kwargs)


class HelpColorsCommand(HelpColorsMixin, click.Command):
    """Click help formatting plugin. See file docstring for license.

    Modified from original copy to support click.style() instead of
    direct ANSII string formatting.
    """

    def __init__(self, *args, **kwargs):
        """Initialize command formatter."""
        super().__init__(*args, **kwargs)
