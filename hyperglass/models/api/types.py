"""Custom validation types."""

import typing as t

from pydantic import AfterValidator

# Project
from hyperglass.constants import SUPPORTED_QUERY_TYPES


def validate_query_type(value: str) -> str:
    """Ensure query type is supported by hyperglass."""
    if value not in SUPPORTED_QUERY_TYPES:
        raise ValueError("'{}' is not a supported query type".format(value))
    return value


SupportedQuery = t.Annotated[str, AfterValidator(validate_query_type)]
