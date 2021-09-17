"""Data models used throughout hyperglass."""

# Standard Library
import re
import typing as t
from pathlib import Path

# Third Party
from pydantic import HttpUrl, BaseModel, BaseConfig, PrivateAttr
from pydantic.generics import GenericModel

# Project
from hyperglass.log import log
from hyperglass.util import snake_to_camel, repr_from_attrs
from hyperglass.types import Series

MultiModelT = t.TypeVar("MultiModelT", bound=BaseModel)


class HyperglassModel(BaseModel):
    """Base model for all hyperglass configuration models."""

    class Config(BaseConfig):
        """Pydantic model configuration."""

        validate_all = True
        extra = "forbid"
        validate_assignment = True
        allow_population_by_field_name = True
        json_encoders = {HttpUrl: lambda v: str(v), Path: str}

        @classmethod
        def alias_generator(cls: "HyperglassModel", field: str) -> str:
            """Remove unsupported characters from field names.

            Converts any "desirable" seperators to underscore, then removes all
            characters that are unsupported in Python class variable names.
            Also removes leading numbers underscores.
            """
            _replaced = re.sub(r"[\-|\.|\@|\~|\:\/|\s]", "_", field)
            _scrubbed = "".join(re.findall(r"([a-zA-Z]\w+|\_+)", _replaced))
            snake_field = _scrubbed.lower()
            if snake_field != field:
                log.debug(
                    "Model field '{}.{}' was converted from {} to {}",
                    cls.__module__,
                    snake_field,
                    repr(field),
                    repr(snake_field),
                )
            return snake_to_camel(snake_field)

    def _repr_from_attrs(self, attrs: Series[str]) -> str:
        """Alias to `hyperglass.util:repr_from_attrs` in the context of this model."""
        return repr_from_attrs(self, attrs)

    def export_json(self, *args, **kwargs):
        """Return instance as JSON."""

        export_kwargs = {"by_alias": False, "exclude_unset": False}

        for key in kwargs.keys():
            export_kwargs.pop(key, None)

        return self.json(*args, **export_kwargs, **kwargs)

    def export_dict(self, *args, **kwargs):
        """Return instance as dictionary."""

        export_kwargs = {"by_alias": False, "exclude_unset": False}

        for key in kwargs.keys():
            export_kwargs.pop(key, None)

        return self.dict(*args, **export_kwargs, **kwargs)

    def export_yaml(self, *args, **kwargs):
        """Return instance as YAML."""

        # Standard Library
        import json

        # Third Party
        import yaml

        export_kwargs = {
            "by_alias": kwargs.pop("by_alias", False),
            "exclude_unset": kwargs.pop("exclude_unset", False),
        }

        return yaml.safe_dump(json.loads(self.export_json(**export_kwargs)), *args, **kwargs)


class HyperglassModelWithId(HyperglassModel):
    """hyperglass model that is unique by its `id` field."""

    id: str

    def __eq__(self: "HyperglassModelWithId", other: "HyperglassModelWithId") -> bool:
        """Other model is equal to this model."""
        if not isinstance(other, self.__class__):
            return False
        if hasattr(other, "id"):
            return other and self.id == other.id
        return False

    def __ne__(self: "HyperglassModelWithId", other: "HyperglassModelWithId") -> bool:
        """Other model is not equal to this model."""
        return not self.__eq__(other)

    def __hash__(self: "HyperglassModelWithId") -> int:
        """Create a hashed representation of this model's name."""
        return hash(self.id)


class HyperglassMultiModel(GenericModel, t.Generic[MultiModelT]):
    """Extension of HyperglassModel for managing multiple models as a list."""

    __root__: t.List[MultiModelT] = []
    _accessor: str = PrivateAttr()
    _model: MultiModelT = PrivateAttr()
    _count: int = PrivateAttr()

    class Config(BaseConfig):
        """Pydantic model configuration."""

        validate_all = True
        extra = "forbid"
        validate_assignment = True

    def __init__(
        self, *items: t.Union[MultiModelT, t.Dict[str, t.Any]], model: MultiModelT, accessor: str
    ) -> None:
        """Validate items."""
        self._accessor = accessor
        self._model = model
        valid = self._valid_items(*items)
        super().__init__(__root__=valid)
        self._count = len(self.__root__)

    def __iter__(self) -> t.Iterator[MultiModelT]:
        """Iterate items."""
        return iter(self.__root__)

    def __getitem__(self, value: t.Union[int, str]) -> MultiModelT:
        """Get an item by accessor value."""
        if not isinstance(value, (str, int)):
            raise TypeError(
                "Value of {}.{!s} should be a string or integer. Got {!r} ({!s})".format(
                    self.__class__.__name__, self.accessor, value, type(value)
                )
            )
        if isinstance(value, int):
            return self.__root__[value]

        for item in self:
            if hasattr(item, self.accessor) and getattr(item, self.accessor) == value:
                return item
        raise IndexError(
            "No match found for {!s}.{!s}={!r}".format(
                self.model.__class__.__name__, self.accessor, value
            ),
        )

    def __repr__(self) -> str:
        """Represent model."""
        return repr_from_attrs(self, ["_count", "_accessor"], strip="_")

    @property
    def accessor(self) -> str:
        """Access item accessor."""
        return self._accessor

    @property
    def model(self) -> MultiModelT:
        """Access item model class."""
        return self._model

    @property
    def count(self) -> int:
        """Access item count."""
        return self._count

    def _valid_items(
        self, *to_validate: t.List[t.Union[MultiModelT, t.Dict[str, t.Any]]]
    ) -> t.List[MultiModelT]:
        items = [
            item
            for item in to_validate
            if any(
                (
                    (isinstance(item, self.model) and hasattr(item, self.accessor)),
                    (isinstance(item, t.Dict) and self.accessor in item),
                ),
            )
        ]
        for index, item in enumerate(items):
            if isinstance(item, t.Dict):
                items[index] = self.model(**item)
        return items

    def add(self, *items, unique_by: t.Optional[str] = None) -> None:
        """Add an item to the model."""
        to_add = self._valid_items(*items)
        if unique_by is not None:
            unique_by_values = {
                getattr(obj, unique_by) for obj in (*self, *to_add) if hasattr(obj, unique_by)
            }
            unique_by_objects = {
                v: o
                for v in unique_by_values
                for o in (*self, *to_add)
                if getattr(o, unique_by) == v
            }
            new: t.List[MultiModelT] = list(unique_by_objects.values())

        else:
            new: t.List[MultiModelT] = [*self.__root__, *to_add]
        self.__root__ = new
        self._count = len(self.__root__)
        for item in new:
            log.debug(
                "Added {} '{!s}' to {}",
                item.__class__.__name__,
                getattr(item, self.accessor),
                self.__class__.__name__,
            )
