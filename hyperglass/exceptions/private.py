"""Internal/private exceptions."""

# Standard Library
from typing import Any, Dict, List

# Local
from ._common import ErrorLevel, PrivateHyperglassError


class ExternalError(PrivateHyperglassError):
    """Raised when an error during a connection to an external service occurs."""

    def __init__(self, message: str, level: ErrorLevel, **kwargs: Dict[str, Any]) -> None:
        """Set level according to level argument."""
        self._level = level
        super().__init__(message, **kwargs)


class UnsupportedDevice(PrivateHyperglassError):
    """Raised when an input NOS is not in the supported NOS list."""

    def __init__(self, device_type: str) -> None:
        """Show the unsupported device type and a list of supported drivers."""
        # Third Party
        from netmiko.ssh_dispatcher import CLASS_MAPPER  # type: ignore

        # Project
        from hyperglass.constants import DRIVER_MAP

        drivers = ("", *[*DRIVER_MAP.keys(), *CLASS_MAPPER.keys()].sort())
        driver_list = "\n  - ".join(drivers)
        super().__init__(message=f"'{device_type}' is not supported. Must be one of:{driver_list}")


class InputValidationError(PrivateHyperglassError):
    """Raised when a validation check fails.

    This needs to be separate from `hyperglass.exceptions.public` for
    circular import reasons.
    """

    kwargs: Dict[str, Any]

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """Set kwargs instance attribute so it can be consumed later.

        `hyperglass.exceptions.public.InputInvalid` will be raised from
        these kwargs.
        """
        self.kwargs = kwargs
        super().__init__(message="", **kwargs)


class ConfigInvalid(PrivateHyperglassError):
    """Raised when a config item fails type or option validation."""

    def __init__(self, errors: List[Dict[str, Any]]) -> None:
        """Parse Pydantic ValidationError."""

        super().__init__(message=self._parse_pydantic_errors(*errors))


class ConfigMissing(PrivateHyperglassError):
    """Raised when a required config file or item is missing or undefined."""

    def __init__(self, missing_item: Any) -> None:
        """Show the missing configuration item."""
        super().__init__(
            (
                "{item} is missing or undefined and is required to start hyperglass. "
                "Please consult the installation documentation."
            ),
            item=missing_item,
        )


class ConfigError(PrivateHyperglassError):
    """Raised for generic user-config issues."""


class UnsupportedError(PrivateHyperglassError):
    """Raised when an unsupported action or request occurs."""


class ParsingError(PrivateHyperglassError):
    """Raised when there is a problem parsing a structured response."""


class DependencyError(PrivateHyperglassError):
    """Raised when a dependency is missing, not running, or on the wrong version."""


class PluginError(PrivateHyperglassError):
    """Raised when a plugin error occurs."""


class StateError(PrivateHyperglassError):
    """Raised when an error occurs while fetching state from Redis."""
