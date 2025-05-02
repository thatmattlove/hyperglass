"""Internal/private exceptions."""

# Standard Library
from typing import Any, Dict, List
from pathlib import Path

# Project
from hyperglass.constants import CONFIG_EXTENSIONS

# Local
from ._common import ErrorLevel, PrivateHyperglassError


class ExternalError(PrivateHyperglassError):
    """Raised when an error during a connection to an external service occurs."""

    def __init__(self, message: str, level: ErrorLevel, **kwargs: Dict[str, Any]) -> None:
        """Set level according to level argument."""
        self._level = level
        super().__init__(message, **kwargs)


class UnsupportedDevice(PrivateHyperglassError):
    """Raised when an input platform is not in the supported platform list."""

    def __init__(self, platform: str) -> None:
        """Show the unsupported device type and a list of supported drivers."""
        # Third Party
        from netmiko.ssh_dispatcher import CLASS_MAPPER  # type: ignore

        # Project
        from hyperglass.constants import DRIVER_MAP

        sorted_drivers = sorted([*DRIVER_MAP.keys(), *CLASS_MAPPER.keys()])
        driver_list = "\n  - ".join(("", *sorted_drivers))
        super().__init__(message=f"'{platform}' is not supported. Must be one of:{driver_list}")


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

    def __init__(self, file_name: str, *, app_path: Path) -> None:
        """Customize error message."""
        message = " ".join(
            (
                file_name.capitalize(),
                "file is missing in",
                f"'{app_path!s}', and is required to start hyperglass.",
                "Supported file names are:",
                ", ".join(f"'{file_name}.{e}'" for e in CONFIG_EXTENSIONS),
                ". Please consult the installation documentation.",
            )
        )
        super().__init__(message)


class ConfigLoaderMissing(PrivateHyperglassError):
    """Raised when a configuration file is using a file extension that requires a missing loader."""

    def __init__(self, path: Path, /) -> None:
        """Customize error message."""
        message = "'{path}' requires a {loader} loader, but it is not installed"
        super().__init__(message=message, path=path, loader=path.suffix.strip("."))


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
