"""Base Plugin Definition."""

# Standard Library
from abc import ABC
from typing import Any, Union, Literal
from inspect import Signature

# Third Party
from pydantic import BaseModel

PluginType = Union[Literal["output"], Literal["input"]]


class HyperglassPlugin(BaseModel, ABC):
    """Plugin to interact with device command output."""

    name: str

    @property
    def _signature(self) -> Signature:
        """Get this instance's class signature."""
        return self.__class__.__signature__

    def __eq__(self, other: "HyperglassPlugin"):
        """Other plugin is equal to this plugin."""
        return other and self._signature == other._signature

    def __ne__(self, other: "HyperglassPlugin"):
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
