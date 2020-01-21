"""hyperglass cli module."""
import stackprinter

# Project Imports
from cli import commands
from cli import echo  # noqa: F401
from cli import formatting  # noqa: F401
from cli import static  # noqa: F401
from cli import util  # noqa: F401

stackprinter.set_excepthook(style="darkbg2")

CLI = commands.hg
