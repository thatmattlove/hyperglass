"""Custom validation types."""

# Project
from hyperglass.constants import SUPPORTED_QUERY_TYPES


class SupportedQuery(str):
    """Query Type Validation Model."""

    @classmethod
    def __get_validators__(cls):
        """Pydantic custom type method."""
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """Ensure query type is supported by hyperglass."""
        if not isinstance(value, str):
            raise TypeError("query_type must be a string")
        if value not in SUPPORTED_QUERY_TYPES:
            raise ValueError(f"'{value}' is not a supported query type")
        return value

    def __repr__(self):
        """Stringify custom field representation."""
        return f"SupportedQuery({super().__repr__()})"
