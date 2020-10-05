"""Static string definitions."""
# Third Party
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

    BUTTERFLY = "\U0001F98B "
    CHECK = "\U00002705 "
    INFO = "\U00002755 "
    ERROR = "\U0000274C "
    WARNING = "\U000026A0\U0000FE0F  "
    TOOLBOX = "\U0001F9F0 "
    NUMBERS = "\U0001F522 "
    FOLDED_HANDS = "\U0001F64F "
    ROCKET = "\U0001F680 "
    SPARKLES = "\U00002728 "
    PAPERCLIP = "\U0001F4CE "
    KEY = "\U0001F511 "
    LOCK = "\U0001F512 "
    CLAMP = "\U0001F5DC "
    BOOKS = "\U0001F4DA "
    THERMOMETER = "\U0001F321 "
    SOAP = "\U0001F9FC "


WS = Char(" ")
NL = Char("\n")
CL = Char(":")
E = Emoji()

CLI_HELP = (
    click.style("hyperglass", fg="magenta", bold=True)
    + WS[1]
    + click.style("Command Line Interface", fg="white")
)

# Click Style Helpers
SUCCESS = {"fg": "green", "bold": True}
WARNING = {"fg": "yellow"}
ERROR = {"fg": "red", "bold": True}
LABEL = {"fg": "white"}
INFO = {"fg": "blue", "bold": True}
STATUS = {"fg": "black"}
VALUE = {"fg": "magenta", "bold": True}
CMD_HELP = {"fg": "white"}


class Message:
    """Helper class for single-character strings."""

    colors = {
        "warning": "yellow",
        "success": "green",
        "error": "red",
        "info": "blue",
        "status": "black",
        "label": "white",
    }
    label_colors = {
        "warning": "yellow",
        "success": "green",
        "error": "red",
        "info": "blue",
        "status": "black",
        "label": "magenta",
    }
    emojis = {
        "warning": E.WARNING,
        "success": E.CHECK,
        "error": E.ERROR,
        "info": E.INFO,
        "status": "",
        "label": "",
    }

    def __init__(self, state):
        """Set instance character."""
        self.state = state
        self.color = self.colors[self.state]
        self.label_color = self.label_colors[self.state]

    @property
    def msg(self):
        """Click style attributes for message text."""
        return {"fg": self.color}

    @property
    def kw(self):
        """Click style attributes for keywords."""
        return {"fg": self.label_color, "bold": True, "underline": True}

    @property
    def emoji(self):
        """Match emoji from state."""
        return self.emojis[self.state]

    def __repr__(self):
        """Stringify the instance character for representation."""
        return "Message(msg={m}, kw={k}, emoji={e})".format(
            m=self.msg, k=self.kw, e=self.emoji
        )
