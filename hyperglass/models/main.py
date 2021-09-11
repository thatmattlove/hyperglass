"""Data models used throughout hyperglass."""

# Standard Library
import re
from pathlib import Path

# Third Party
from pydantic import HttpUrl, BaseModel, BaseConfig

# Project
from hyperglass.log import log
from hyperglass.util import snake_to_camel


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

        return yaml.safe_dump(
            json.loads(self.export_json(**export_kwargs)), *args, **kwargs
        )
