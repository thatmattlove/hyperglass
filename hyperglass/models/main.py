"""Data models used throughout hyperglass."""

# Standard Library
import re
from typing import Type, TypeVar

# Third Party
from pydantic import HttpUrl, BaseModel

# Project
from hyperglass.util import snake_to_camel


def clean_name(_name: str) -> str:
    """Remove unsupported characters from field names.

    Converts any "desirable" seperators to underscore, then removes all
    characters that are unsupported in Python class variable names.
    Also removes leading numbers underscores.
    """
    _replaced = re.sub(r"[\-|\.|\@|\~|\:\/|\s]", "_", _name)
    _scrubbed = "".join(re.findall(r"([a-zA-Z]\w+|\_+)", _replaced))
    return _scrubbed.lower()


AsUIModel = TypeVar("AsUIModel", bound="BaseModel")


class HyperglassModel(BaseModel):
    """Base model for all hyperglass configuration models."""

    class Config:
        """Pydantic model configuration.

        See https://pydantic-docs.helpmanual.io/usage/model_config
        """

        validate_all = True
        extra = "forbid"
        validate_assignment = True
        alias_generator = clean_name
        json_encoders = {HttpUrl: lambda v: str(v)}

    def export_json(self, *args, **kwargs):
        """Return instance as JSON."""

        export_kwargs = {"by_alias": True, "exclude_unset": False}

        for key in export_kwargs.keys():
            export_kwargs.pop(key, None)

        return self.json(*args, **export_kwargs, **kwargs)

    def export_dict(self, *args, **kwargs):
        """Return instance as dictionary."""

        export_kwargs = {"by_alias": True, "exclude_unset": False}

        for key in export_kwargs.keys():
            export_kwargs.pop(key, None)

        return self.dict(*args, **export_kwargs, **kwargs)

    def export_yaml(self, *args, **kwargs):
        """Return instance as YAML."""

        # Standard Library
        import json

        # Third Party
        import yaml

        export_kwargs = {
            "by_alias": kwargs.pop("by_alias", True),
            "exclude_unset": kwargs.pop("by_alias", False),
        }

        return yaml.safe_dump(
            json.loads(self.export_json(**export_kwargs)), *args, **kwargs
        )


class HyperglassModelExtra(HyperglassModel):
    """Model for hyperglass configuration models with dynamic fields."""

    class Config:
        """Pydantic model configuration."""

        extra = "allow"


class HyperglassUIModel(HyperglassModel):
    """Base class for UI configuration parameters."""

    class Config:
        """Pydantic model configuration."""

        alias_generator = snake_to_camel
        allow_population_by_field_name = True


def as_ui_model(name: str, model: Type[AsUIModel]) -> Type[AsUIModel]:
    """Override a model's configuration to confirm to a UI model."""
    return type(name, (model, HyperglassUIModel), {})
