# Standard Library
import re
from typing import TypeVar

# Third Party
from pydantic import HttpUrl, BaseModel, StrictInt, StrictFloat

# Project
from hyperglass.util import clean_name

IntFloat = TypeVar("IntFloat", StrictInt, StrictFloat)


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
        return self.json(by_alias=True, exclude_unset=False, *args, **kwargs)

    def export_dict(self, *args, **kwargs):
        """Return instance as dictionary.

        Returns:
            {dict} -- Python dictionary.
        """
        return self.dict(by_alias=True, exclude_unset=False, *args, **kwargs)

    def export_yaml(self, *args, **kwargs):
        """Return instance as YAML.

        Returns:
            {str} -- Stringified YAML.
        """
        import json
        import yaml

        return yaml.safe_dump(json.loads(self.export_json()), *args, **kwargs)


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


class StrictBytes(bytes):
    """Custom data type for a strict byte string.

    Used for validating the encoded JWT request payload.
    """

    @classmethod
    def __get_validators__(cls):
        """Yield Pydantic validator function.

        See: https://pydantic-docs.helpmanual.io/usage/types/#custom-data-types

        Yields:
            {function} -- Validator
        """
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """Validate type.

        Arguments:
            value {Any} -- Pre-validated input

        Raises:
            TypeError: Raised if value is not bytes

        Returns:
            {object} -- Instantiated class
        """
        if not isinstance(value, bytes):
            raise TypeError("bytes required")
        return cls()

    def __repr__(self):
        """Return representation of object.

        Returns:
            {str} -- Representation
        """
        return f"StrictBytes({super().__repr__()})"
