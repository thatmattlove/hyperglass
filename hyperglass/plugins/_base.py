"""Base Plugin Definition."""

# Standard Library
import typing as t
from abc import ABC
from inspect import Signature

# Third Party
from pydantic import BaseModel, PrivateAttr

# Project
from hyperglass.log import log as _logger

if t.TYPE_CHECKING:
    # Third Party
    from loguru import Logger

PluginType = t.Union[t.Literal["output"], t.Literal["input"]]
SupportedMethod = t.TypeVar("SupportedMethod")


class HyperglassPlugin(BaseModel, ABC):
    """Plugin to interact with device command output."""

    _hyperglass_builtin: bool = PrivateAttr(False)
    _type: t.ClassVar[str]
    name: str
    common: bool = False
    ref: t.Optional[str] = None
    log: t.ClassVar["Logger"] = _logger

    @property
    def _signature(self) -> Signature:
        """Get this instance's class signature."""
        return self.__class__.__signature__

    def __eq__(self, other: "HyperglassPlugin") -> bool:
        """Other plugin is equal to this plugin."""
        if hasattr(other, "_signature"):
            return other and self._signature == other._signature
        return False

    def __ne__(self, other: "HyperglassPlugin") -> bool:
        """Other plugin is not equal to this plugin."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Create a hashed representation of this plugin's name."""
        return hash(self._signature)

    def __str__(self) -> str:
        """Represent plugin by its name."""
        return self.name

    @classmethod
    def __init_subclass__(cls, **kwargs: t.Any) -> None:
        """Initialize plugin object."""
        name = kwargs.pop("name", None) or cls.__name__
        cls.name = name
        super().__init_subclass__()

    def __init__(self, **kwargs: t.Any) -> None:
        """Initialize plugin instance."""
        name = kwargs.pop("name", None) or self.__class__.__name__
        super().__init__(name=name, **kwargs)

    def __rich_console__(self, *_, **__):
        """Create a rich representation of this plugin for the hyperglass CLI."""

        # Third Party
        from rich.text import Text
        from rich.panel import Panel
        from rich.table import Table
        from rich.pretty import Pretty

        table = Table.grid(padding=(0, 1), expand=False)
        table.add_column(justify="right")

        data = {"builtin": True if self._hyperglass_builtin else False}
        data.update(
            {
                attr: getattr(self, attr)
                for attr in ("name", "common", "directives", "platforms")
                if hasattr(self, attr)
            }
        )
        data = {k: data[k] for k in sorted(data.keys())}
        for key, value in data.items():
            table.add_row(
                Text.assemble((key, "inspect.attr"), (" =", "inspect.equals")), Pretty(value)
            )

        yield Panel(
            table,
            expand=False,
            title=f"[bold magenta]{self.name}",
            title_align="left",
            subtitle=f"[bold cornflower_blue]{self._type.capitalize()} Plugin",
            subtitle_align="right",
            padding=(1, 3),
        )


class DirectivePlugin(BaseModel):
    """Plugin associated with directives.

    Should always be subclassed with `HyperglassPlugin`.
    """

    directives: t.Sequence[str] = ()


class PlatformPlugin(BaseModel):
    """Plugin associated with specific device platform.

    Should always be subclassed with `HyperglassPlugin`.
    """

    platforms: t.Sequence[str] = ()
