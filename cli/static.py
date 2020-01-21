"""Static string definitions."""
# Third Party Imports
import click


class Char:
    """Helper class for single-character strings."""

    def __init__(self, char):
        """Set instance character."""
        self.char = char

    def __getitem__(self, i):
        """Subscription returns the instance's character * n."""
        return self.char * i

    def __str__(self):
        """Stringify the instance character."""
        return str(self.char)

    def __repr__(self):
        """Stringify the instance character for representation."""
        return str(self.char)

    def __add__(self, other):
        """Addition method for string concatenation."""
        return str(self.char) + str(other)


class Emoji:
    """Helper class for unicode emoji."""

    BUTTERFLY = "\U0001F98B" + " "
    CHECK = "\U00002705" + " "
    INFO = "\U00002755"
    ERROR = "\U0000274C" + " "
    ROCKET = "\U0001F680" + " "
    SPARKLES = "\U00002728" + " "
    PAPERCLIP = "\U0001F4CE" + " "
    KEY = "\U0001F511"
    LOCK = "\U0001F512"
    CLAMP = "\U0001F5DC" + " "


WS = Char(" ")
NL = Char("\n")
CL = Char(":")
E = Emoji()

CLI_HELP = (
    click.style("hyperglass", fg="magenta", bold=True)
    + WS[1]
    + click.style("CLI Management Tool", fg="white")
)

# Click Style Helpers
SUCCESS = {"fg": "green", "bold": True}
ERROR = {"fg": "red", "bold": True}
LABEL = {"fg": "white"}
INFO = {"fg": "blue", "bold": True}
STATUS = {"fg": "black"}
VALUE = {"fg": "magenta", "bold": True}
CMD_HELP = {"fg": "white"}
