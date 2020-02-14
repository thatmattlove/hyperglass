"""hyperglass cli module."""
# Third Party
import stackprinter

# Project
from hyperglass.cli import commands

stackprinter.set_excepthook(style="darkbg2")

CLI = commands.hg
