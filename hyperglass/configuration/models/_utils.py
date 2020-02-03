"""Utility Functions for Pydantic Models."""

# Standard Library
import re

# Third Party
from pydantic import BaseModel


def clean_name(_name):
    """Remove unsupported characters from field names.

    Converts any "desirable" seperators to underscore, then removes all
    characters that are unsupported in Python class variable names.
    Also removes leading numbers underscores.

    Arguments:
        _name {str} -- Initial field name

    Returns:
        {str} -- Cleaned field name
    """
    _replaced = re.sub(r"[\-|\.|\@|\~|\:\/|\s]", "_", _name)
    _scrubbed = "".join(re.findall(r"([a-zA-Z]\w+|\_+)", _replaced))
    return _scrubbed.lower()


class HyperglassModel(BaseModel):
    """Base model for all hyperglass configuration models."""

    pass

    class Config:
        """Default Pydantic configuration.

        See https://pydantic-docs.helpmanual.io/usage/model_config
        """

        validate_all = True
        extra = "forbid"
        validate_assignment = True
        alias_generator = clean_name


class HyperglassModelExtra(HyperglassModel):
    """Model for hyperglass configuration models with dynamic fields."""

    pass

    class Config:
        """Default pydantic configuration."""

        extra = "allow"


class AnyUri(str):
    """Custom field type for HTTP URI, e.g. /example."""

    @classmethod
    def __get_validators__(cls):
        """Pydantic custim field method."""
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """Ensure URI string contains a leading forward-slash."""
        uri_regex = re.compile(r"^(\/.*)$")
        if not isinstance(value, str):
            raise TypeError("AnyUri type must be a string")
        match = uri_regex.fullmatch(value)
        if not match:
            raise ValueError(
                "Invalid format. A URI must begin with a forward slash, e.g. '/example'"
            )
        return cls(match.group())

    def __repr__(self):
        """Stringify custom field representation."""
        return f"AnyUri({super().__repr__()})"
