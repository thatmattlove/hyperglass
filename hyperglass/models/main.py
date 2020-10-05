"""Data models used throughout hyperglass."""

# Standard Library
import re

# Third Party
from pydantic import HttpUrl, BaseModel

_WEBHOOK_TITLE = "hyperglass received a valid query with the following data"
_ICON_URL = "https://res.cloudinary.com/hyperglass/image/upload/v1593192484/icon.png"


def clean_name(_name: str) -> str:
    """Remove unsupported characters from field names.

    Converts any "desirable" seperators to underscore, then removes all
    characters that are unsupported in Python class variable names.
    Also removes leading numbers underscores.
    """
    _replaced = re.sub(r"[\-|\.|\@|\~|\:\/|\s]", "_", _name)
    _scrubbed = "".join(re.findall(r"([a-zA-Z]\w+|\_+)", _replaced))
    return _scrubbed.lower()


class HyperglassModel(BaseModel):
    """Base model for all hyperglass configuration models."""

    class Config:
        """Default Pydantic configuration.

        See https://pydantic-docs.helpmanual.io/usage/model_config
        """

        validate_all = True
        extra = "forbid"
        validate_assignment = True
        alias_generator = clean_name
        json_encoders = {HttpUrl: lambda v: str(v)}

    def export_json(self, *args, **kwargs):
        """Return instance as JSON.

        Returns:
            {str} -- Stringified JSON.
        """

        export_kwargs = {
            "by_alias": True,
            "exclude_unset": False,
            **kwargs,
        }

        return self.json(*args, **export_kwargs)

    def export_dict(self, *args, **kwargs):
        """Return instance as dictionary.

        Returns:
            {dict} -- Python dictionary.
        """
        export_kwargs = {
            "by_alias": True,
            "exclude_unset": False,
            **kwargs,
        }

        return self.dict(*args, **export_kwargs)

    def export_yaml(self, *args, **kwargs):
        """Return instance as YAML.

        Returns:
            {str} -- Stringified YAML.
        """
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

    pass

    class Config:
        """Default pydantic configuration."""

        extra = "allow"
