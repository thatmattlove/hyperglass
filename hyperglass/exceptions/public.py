"""User-facing/Public exceptions."""

# Standard Library
from typing import TYPE_CHECKING, Any, Dict, Optional

# Local
from ._common import PublicHyperglassError

if TYPE_CHECKING:
    # Project
    from hyperglass.models.api.query import Query
    from hyperglass.models.config.devices import Device


class ScrapeError(
    PublicHyperglassError,
    template="connection_error",
    level="danger",
):
    """Raised when an SSH driver error occurs."""

    def __init__(self, *, error: BaseException, device: "Device"):
        """Initialize parent error."""
        super().__init__(error=str(error), device=device.name, proxy=device.proxy)


class AuthError(PublicHyperglassError, template="authentication_error", level="danger"):
    """Raised when authentication to a device fails."""

    def __init__(self, *, error: BaseException, device: "Device"):
        """Initialize parent error."""
        super().__init__(error=str(error), device=device.name, proxy=device.proxy)


class RestError(PublicHyperglassError, template="connection_error", level="danger"):
    """Raised upon a rest API client error."""

    def __init__(self, *, error: BaseException, device: "Device"):
        """Initialize parent error."""
        super().__init__(error=str(error), device=device.name)


class DeviceTimeout(PublicHyperglassError, template="request_timeout", level="danger"):
    """Raised when the connection to a device times out."""

    def __init__(self, *, error: BaseException, device: "Device"):
        """Initialize parent error."""
        super().__init__(error=str(error), device=device.name, proxy=device.proxy)


class InvalidQuery(PublicHyperglassError, template="request_timeout"):
    """Raised when input validation fails."""

    def __init__(
        self, *, error: Optional[str] = None, query: "Query", **kwargs: Dict[str, Any]
    ) -> None:
        """Initialize parent error."""

        kwargs = {
            "query_type": query.query_type,
            "target": query.query_target,
            "error": str(error),
            **kwargs,
        }

        super().__init__(**kwargs)


class NotFound(PublicHyperglassError, template="not_found"):
    """Raised when an object is not found."""

    def __init__(self, type: str, name: str, **kwargs: Dict[str, str]) -> None:
        """Initialize parent error."""
        super().__init__(type=type, name=name, **kwargs)


class QueryLocationNotFound(NotFound):
    """Raised when a query location is not found."""

    def __init__(self, location: Any, **kwargs: Dict[str, Any]) -> None:
        """Initialize a NotFound error for a query location."""
        # Project
        from hyperglass.state import use_state

        (text := use_state("params").web.text)

        super().__init__(type=text.query_location, name=str(location), **kwargs)


class QueryTypeNotFound(NotFound):
    """Raised when a query type is not found."""

    def __init__(self, query_type: Any, **kwargs: Dict[str, Any]) -> None:
        """Initialize a NotFound error for a query type."""
        # Project
        from hyperglass.state import use_state

        (text := use_state("params").web.text)
        super().__init__(type=text.query_type, name=str(query_type), **kwargs)


class InputInvalid(PublicHyperglassError, template="invalid_input"):
    """Raised when input validation fails."""

    def __init__(
        self, *, error: Optional[Any] = None, target: str, **kwargs: Dict[str, Any]
    ) -> None:
        """Initialize parent error."""

        kwargs = {"target": target, "error": str(error), **kwargs}

        super().__init__(**kwargs)


class InputNotAllowed(PublicHyperglassError, template="target_not_allowed"):
    """Raised when input validation fails due to a configured check."""

    def __init__(
        self, *, error: Optional[str] = None, query: "Query", **kwargs: Dict[str, Any]
    ) -> None:
        """Initialize parent error."""

        kwargs = {
            "query_type": query.query_type,
            "target": query.query_target,
            "error": str(error),
            **kwargs,
        }

        super().__init__(**kwargs)


class ResponseEmpty(PublicHyperglassError, template="no_output"):
    """Raised when hyperglass can connect to the device but the response is empty."""

    def __init__(
        self, *, error: Optional[str] = None, query: "Query", **kwargs: Dict[str, Any]
    ) -> None:
        """Initialize parent error."""

        kwargs = {
            "query_type": query.query_type,
            "target": query.query_target,
            "error": str(error),
            **kwargs,
        }

        super().__init__(**kwargs)
