"""Data models used throughout hyperglass."""

# Standard Library

# Standard Library
import re
import json
import typing as t
from pathlib import Path

# Third Party
from pydantic import HttpUrl, BaseModel, RootModel, ConfigDict, PrivateAttr

# Project
from hyperglass.log import log
from hyperglass.util import compare_init, snake_to_camel, repr_from_attrs
from hyperglass.types import Series

MultiModelT = t.TypeVar("MultiModelT", bound=BaseModel)

PathTypeT = t.TypeVar("PathTypeT")


def alias_generator(field: str) -> str:
    """Remove unsupported characters from field names.

    Converts any "desirable" separators to underscore, then removes all
    characters that are unsupported in Python class variable names.
    Also removes leading numbers underscores.
    """
    _replaced = re.sub(r"[\-|\.|\@|\~|\:\/|\s]", "_", field)
    _scrubbed = "".join(re.findall(r"([a-zA-Z]\w+|\_+)", _replaced))
    snake_field = _scrubbed.lower()
    return snake_to_camel(snake_field)


class HyperglassModel(BaseModel):
    """Base model for all hyperglass configuration models."""

    model_config = ConfigDict(
        extra="forbid",
        json_encoders={HttpUrl: lambda v: str(v), Path: str},
        populate_by_name=True,
        validate_assignment=True,
        validate_default=True,
        alias_generator=alias_generator,
    )

    def convert_paths(self, value: t.Type[PathTypeT]) -> PathTypeT:
        """Change path to relative to app_path.

        This is required when running hyperglass in a container so that
        the original app_path on the host system is not passed through
        to the container.
        """
        # Project
        from hyperglass.settings import Settings

        if isinstance(value, Path):
            if Settings.container:
                return Settings.default_app_path.joinpath(
                    *(
                        p
                        for p in value.parts
                        if p not in Settings.original_app_path.absolute().parts
                    )
                )

        if isinstance(value, str) and str(Settings.original_app_path.absolute()) in value:
            if Settings.container:
                path = Path(value)
                return str(
                    Settings.default_app_path.joinpath(
                        *(
                            p
                            for p in path.parts
                            if p not in Settings.original_app_path.absolute().parts
                        )
                    )
                )

        if isinstance(value, t.Tuple):
            return tuple(self.convert_paths(v) for v in value)
        if isinstance(value, t.List):
            return [self.convert_paths(v) for v in value]
        if isinstance(value, t.Generator):
            return (self.convert_paths(v) for v in value)
        if isinstance(value, t.Dict):
            return {k: self.convert_paths(v) for k, v in value.items()}
        return value

    def _repr_from_attrs(self, attrs: Series[str]) -> str:
        """Alias to `hyperglass.util:repr_from_attrs` in the context of this model."""
        return repr_from_attrs(self, attrs)

    def export_json(self, *args, **kwargs):
        """Return instance as JSON."""

        export_kwargs = {"by_alias": False, "exclude_unset": False}

        for key in kwargs.keys():
            export_kwargs.pop(key, None)

        return self.model_dump_json(*args, **export_kwargs, **kwargs)

    def export_dict(self, *args, **kwargs):
        """Return instance as dictionary."""

        export_kwargs = {"by_alias": False, "exclude_unset": False}

        for key in kwargs.keys():
            export_kwargs.pop(key, None)

        return self.model_dump(*args, **export_kwargs, **kwargs)

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


class HyperglassUniqueModel(HyperglassModel):
    """hyperglass model that is unique by its `id` field."""

    _unique_fields: t.ClassVar[Series[str]] = ()

    def __init_subclass__(cls, *, unique_by: Series[str], **kw: t.Any) -> None:
        """Assign unique fields to class."""
        cls._unique_fields = tuple(unique_by)
        return super().__init_subclass__(**kw)

    def __eq__(self: "HyperglassUniqueModel", other: "HyperglassUniqueModel") -> bool:
        """Other model is equal to this model."""
        if not isinstance(other, self.__class__):
            return False
        if hash(self) == hash(other):
            return True
        return False

    def __ne__(self: "HyperglassUniqueModel", other: "HyperglassUniqueModel") -> bool:
        """Other model is not equal to this model."""
        return not self.__eq__(other)

    def __hash__(self: "HyperglassUniqueModel") -> int:
        """Create a hashed representation of this model's name."""
        fields = dict(zip(self._unique_fields, (getattr(self, f) for f in self._unique_fields)))
        return hash(json.dumps(fields))


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


class MultiModel(RootModel[MultiModelT]):
    """Extension of HyperglassModel for managing multiple models as a list."""

    model_config = ConfigDict(
        validate_default=True,
        validate_assignment=True,
    )

    model: t.ClassVar[MultiModelT]
    unique_by: t.ClassVar[str]
    _model_name: t.ClassVar[str] = "MultiModel"

    root: t.List[MultiModelT] = []
    _count: int = PrivateAttr()

    def __init__(self, *items: t.Union[MultiModelT, t.Dict[str, t.Any]]) -> None:
        """Validate items."""
        for cls_var in ("model", "unique_by"):
            if getattr(self, cls_var, None) is None:
                raise AttributeError(f"MultiModel is missing class variable '{cls_var}'")
        valid = self._valid_items(*items)
        super().__init__(root=valid)
        self._count = len(self.root)

    def __init_subclass__(cls, **kw: t.Any) -> None:
        """Add class variables from keyword arguments."""
        model = kw.pop("model", None)
        cls.model = model
        cls.unique_by = kw.pop("unique_by", None)
        cls._model_name = getattr(model, "__name__", "MultiModel")
        super().__init_subclass__()

    def __repr__(self) -> str:
        """Represent model."""
        return repr_from_attrs(self, ["_count", "unique_by", "_model_name"], strip="_")

    def __iter__(self) -> t.Iterator[MultiModelT]:
        """Iterate items."""
        return iter(self.root)

    def __getitem__(self, value: t.Union[int, str]) -> MultiModelT:
        """Get an item by its `unique_by` property."""
        if not isinstance(value, (str, int)):
            raise TypeError(
                "Value of {}.{!s} should be a string or integer. Got {!r} ({!s})".format(
                    self.__class__.__name__, self.unique_by, value, type(value)
                )
            )
        if isinstance(value, int):
            return self.root[value]

        for item in self:
            if hasattr(item, self.unique_by) and getattr(item, self.unique_by) == value:
                return item
        raise IndexError(
            "No match found for {!s}.{!s}={!r}".format(
                self.model.__class__.__name__, self.unique_by, value
            ),
        )

    def __add__(self, other: MultiModelT) -> MultiModelT:
        """Merge another MultiModel with this one.

        Note: If you're subclassing `HyperglassMultiModel` and overriding `__init__`, you need to
        override this too.
        """
        valid = all(
            (
                isinstance(other, self.__class__),
                hasattr(other, "model"),
                getattr(other, "model", None) == self.model,
            ),
        )
        if not valid:
            raise TypeError(f"Cannot add {other!r} to {self.__class__.__name__}")
        merged = self._merge_with(*other, unique_by=self.unique_by)

        if compare_init(self.__class__, other.__class__):
            return self.__class__(*merged)
        raise TypeError(
            f"{self.__class__.__name__} and {other.__class__.__name__} have different `__init__` "
            "signatures. You probably need to override `MultiModel.__add__`"
        )

    def __len__(self) -> int:
        """Get number of items."""
        return len(self.root)

    @property
    def ids(self) -> t.Tuple[t.Any, ...]:
        """Get values of all items by `unique_by` property."""
        return tuple(sorted(getattr(item, self.unique_by) for item in self))

    @property
    def count(self) -> int:
        """Access item count."""
        return self._count

    @classmethod
    def create(cls, name: str, *, model: MultiModelT, unique_by: str) -> "MultiModel":
        """Create a MultiModel."""
        new = type(name, (cls,), cls.__dict__)
        new.model = model
        new.unique_by = unique_by
        new._model_name = getattr(model, "__name__", "MultiModel")
        return new

    def _valid_items(
        self, *to_validate: t.List[t.Union[MultiModelT, t.Dict[str, t.Any]]]
    ) -> t.List[MultiModelT]:
        items = [
            item
            for item in to_validate
            if any(
                (
                    (isinstance(item, self.model) and hasattr(item, self.unique_by)),
                    (isinstance(item, t.Dict) and self.unique_by in item),
                ),
            )
        ]
        for index, item in enumerate(items):
            if isinstance(item, t.Dict):
                items[index] = self.model(**item)
        return items

    def _merge_with(self, *items, unique_by: t.Optional[str] = None) -> Series[MultiModelT]:
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
            return tuple(unique_by_objects.values())
        return (*self.root, *to_add)

    def filter(self, *properties: str) -> MultiModelT:
        """Get only items with `unique_by` properties matching values in `properties`."""
        return self.__class__(
            *(item for item in self if getattr(item, self.unique_by, None) in properties)
        )

    def matching(self, *unique: str) -> MultiModelT:
        """Get a new instance containing partial matches from `accessors`."""

        def matches(*searches: str) -> t.Generator[MultiModelT, None, None]:
            """Get any matching items by unique_by property.

            For example, if `unique` is `('one', 'two')`, and `Model.<unique_by>` is `'one'`,
            `Model` is yielded.
            """
            for search in searches:
                pattern = re.compile(rf".*{search}.*", re.IGNORECASE)
                for item in self:
                    if pattern.match(getattr(item, self.unique_by)):
                        yield item

        return self.__class__(*matches(*unique))

    def add(self, *items, unique_by: t.Optional[str] = None) -> None:
        """Add an item to the model."""
        new = self._merge_with(*items, unique_by=unique_by)
        self.root = new
        self._count = len(self.root)
        for item in new:
            log.debug(
                "Added {} '{!s}' to {}".format(
                    item.__class__.__name__,
                    getattr(item, self.unique_by),
                    self.__class__.__name__,
                )
            )
