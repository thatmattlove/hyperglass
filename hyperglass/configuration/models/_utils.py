"""Utility Functions for Pydantic Models."""

# Standard Library
import os
import re
from pathlib import Path

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


def validate_image(value):
    """Convert file path to URL path.

    Arguments:
        value {FilePath} -- Path to logo file.

    Returns:
        {str} -- Formatted logo path
    """
    base_path = value.split("/")

    if base_path[0] == "/":
        value = "/".join(base_path[1:])

    if base_path[0] not in ("images", "custom"):
        raise ValueError(
            "Logo files must be in the 'custom/' directory of your hyperglass directory. Got: {f}",
            f=value,
        )

    if base_path[0] == "custom":
        config_path = Path(os.environ["hyperglass_directory"])
        custom_file = config_path / "static" / value

        if not custom_file.exists():
            raise ValueError("'{f}' does not exist", f=str(custom_file))

    return value
