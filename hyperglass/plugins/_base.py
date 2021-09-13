"""Base Plugin Definition."""

# Standard Library
from abc import ABC
from typing import Any, Union, Literal, TypeVar, Sequence
from inspect import Signature

# Third Party
from pydantic import BaseModel, PrivateAttr

PluginType = Union[Literal["output"], Literal["input"]]
SupportedMethod = TypeVar("SupportedMethod")


class HyperglassPlugin(BaseModel, ABC):
    """Plugin to interact with device command output."""

    __hyperglass_builtin__: bool = PrivateAttr(False)
    name: str

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
    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize plugin object."""
        name = kwargs.pop("name", None) or cls.__name__
        cls._name = name
        super().__init_subclass__()

    def __init__(self, **kwargs: Any) -> None:
        """Initialize plugin instance."""
        name = kwargs.pop("name", None) or self.__class__.__name__
        super().__init__(name=name, **kwargs)


class DirectivePlugin(HyperglassPlugin):
    """Plugin associated with directives."""

    directives: Sequence[str] = ()
