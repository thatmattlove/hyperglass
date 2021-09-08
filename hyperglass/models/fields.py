"""Custom Pydantic Fields/Types."""

# Standard Library
import re
from typing import TypeVar

# Third Party
from pydantic import StrictInt, StrictFloat, constr

IntFloat = TypeVar("IntFloat", StrictInt, StrictFloat)

SupportedDriver = constr(regex=r"(scrapli|netmiko|hyperglass_agent)")


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


class AnyUri(str):
    """Custom field type for HTTP URI, e.g. /example."""

    @classmethod
    def __get_validators__(cls):
        """Pydantic custom field method."""
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


class Action(str):
    """Custom field type for policy actions."""

    permits = ("permit", "allow", "accept")
    denies = ("deny", "block", "reject")

    @classmethod
    def __get_validators__(cls):
        """Pydantic custom field method."""
        yield cls.validate

    @classmethod
    def validate(cls, value: str):
        """Ensure action is an allowed value or acceptable alias."""
        if not isinstance(value, str):
            raise TypeError("Action type must be a string")
        value = value.strip().lower()

        if value in cls.permits:
            return cls("permit")
        elif value in cls.denies:
            return cls("deny")

        raise ValueError(
            "Action must be one of '{}'".format(", ".join((*cls.permits, *cls.denies)))
        )

    def __repr__(self):
        """Stringify custom field representation."""
        return f"Action({super().__repr__()})"
