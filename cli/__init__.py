"""hyperglass cli module."""
# Third Party
import stackprinter

# Project
from cli import echo, util, static, commands, formatting, schema  # noqa: F401

stackprinter.set_excepthook(style="darkbg2")

CLI = commands.hg
