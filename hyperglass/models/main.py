"""Data models used throughout hyperglass."""

# Standard Library
import re
from pathlib import Path

# Third Party
from pydantic import HttpUrl, BaseModel, BaseConfig

# Project
from hyperglass.log import log
from hyperglass.util import snake_to_camel, repr_from_attrs
from hyperglass.types import Series


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
