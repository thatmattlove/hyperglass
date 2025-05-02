"""Static string definitions."""

# Third Party
from rich.box import Box

MD_BOX = Box(
    """\
    
| ||
|-||
| ||
|  |
|  |
| ||
    
""",
    ascii=True,
)


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


WS = Char(" ")
NL = Char("\n")
CL = Char(":")
