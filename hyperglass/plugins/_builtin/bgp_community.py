"""Remove anything before the command if found in output."""

# Standard Library
import typing as t
from ipaddress import ip_address

# Third Party
from pydantic import PrivateAttr

# Project
from hyperglass.state.hooks import use_state

# Local
from .._input import InputPlugin

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.api.query import Query

    # Local
    from .._input import InputPluginValidationReturn

_32BIT = 0xFFFFFFFF
_16BIT = 0xFFFF
EXTENDED_TYPES = ("target", "origin")


def check_decimal(value: str, size: int) -> bool:
    """Verify the value is a 32 bit number."""
    try:
        return abs(int(value)) <= size
    except Exception:
        return False


def check_string(value: str) -> bool:
    """Verify part of a community is an IPv4 address, per RFC4360."""
    try:
        addr = ip_address(value)
        return addr.version == 4
    except ValueError:
        return False


def validate_decimal(value: str) -> bool:
    """Verify a community is a 32 bit decimal number."""
    return check_decimal(value, _32BIT)


def validate_new_format(value: str) -> bool:
    """Verify a community matches "new" format, standard or extended."""
    if ":" in value:
        parts = [p for p in value.split(":") if p]
        if len(parts) == 3:
            if parts[0].lower() not in EXTENDED_TYPES:
                # Handle extended community format with `target:` or `origin:` prefix.
                return False
            # Remove type from parts list after it's been validated.
            parts = parts[1:]
        if len(parts) != 2:
            # Only allow two sections in new format, e.g. 65000:1
            return False

        one, two = parts

        if all((check_decimal(one, _16BIT), check_decimal(two, _16BIT))):
            # Handle standard format, e.g. `65000:1`
            return True
        if all((check_decimal(one, _16BIT), check_decimal(two, _32BIT))):
            # Handle extended format, e.g. `65000:4294967295`
            return True
        if all((check_string(one), check_decimal(two, _16BIT))):
            # Handle IP address format, e.g. `192.0.2.1:65000`
            return True

    return False


def validate_large_community(value: str) -> bool:
    """Verify a community matches "large" format. E.g., `65000:65001:65002`."""
    if ":" in value:
        parts = [p for p in value.split(":") if p]
        if len(parts) != 3:
            return False
        for part in parts:
            if not check_decimal(part, _32BIT):
                # Each member must be a 32 bit number.
                return False
        return True
    return False


class ValidateBGPCommunity(InputPlugin):
    """Validate a BGP community string."""

    _hyperglass_builtin: bool = PrivateAttr(True)

    def validate(self, query: "Query") -> "InputPluginValidationReturn":
        """Ensure an input query target is a valid BGP community."""

        params = use_state("params")

        if not isinstance(query.query_target, str):
            return None

        for validator in (validate_decimal, validate_new_format, validate_large_community):
            result = validator(query.query_target)
            if result is True:
                return True

        self.failure_reason = params.messages.invalid_input
        return False
