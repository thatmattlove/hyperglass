"""Custom exceptions for hyperglass."""

# Standard Library
import json as _json
from typing import Any, Dict, List, Union, Literal, Optional

# Project
from hyperglass.log import log
from hyperglass.util import get_fmt_keys
from hyperglass.constants import STATUS_CODE_MAP

ErrorLevel = Literal["danger", "warning"]


class HyperglassError(Exception):
    """hyperglass base exception."""

    def __init__(
        self,
        message: str = "",
        level: ErrorLevel = "warning",
        keywords: Optional[List[str]] = None,
    ) -> None:
        """Initialize the hyperglass base exception class."""
        self._message = message
        self._level = level
        self._keywords = keywords or []
        if self._level == "warning":
            log.error(repr(self))
        elif self._level == "danger":
            log.critical(repr(self))
        else:
            log.info(repr(self))

    def __str__(self) -> str:
        """Return the instance's error message."""
        return self._message

    def __repr__(self) -> str:
        """Return the instance's severity & error message in a string."""
        return f"[{self.level.upper()}] {self._message}"

    def dict(self) -> Dict[str, Union[str, List[str]]]:
        """Return the instance's attributes as a dictionary."""
        return {
            "message": self._message,
            "level": self._level,
            "keywords": self._keywords,
        }

    def json(self) -> str:
        """Return the instance's attributes as a JSON object."""
        return _json.dumps(self.__dict__())

    @staticmethod
    def _safe_format(template: str, **kwargs: Dict[str, str]) -> str:
        """Safely format a string template from keyword arguments."""

        keys = get_fmt_keys(template)
        for key in keys:
            if key not in kwargs:
                kwargs.pop(key)
            else:
                kwargs[key] = str(kwargs[key])
        return template.format(**kwargs)

    def _parse_pydantic_errors(*errors: Dict[str, Any]) -> str:

        errs = ("\n",)

        for err in errors:
            loc = " → ".join(str(loc) for loc in err["loc"])
            errs += (f'Field: {loc}\n  Error: {err["msg"]}\n',)

        return "\n".join(errs)

    @property
    def message(self) -> str:
        """Return the instance's `message` attribute."""
        return self._message

    @property
    def level(self) -> str:
        """Return the instance's `level` attribute."""
        return self._level

    @property
    def keywords(self) -> List[str]:
        """Return the instance's `keywords` attribute."""
        return self._keywords

    @property
    def status_code(self) -> int:
        """Return HTTP status code based on level level."""
        return STATUS_CODE_MAP.get(self._level, 500)


class PublicHyperglassError(HyperglassError):
    """Base exception class for user-facing errors.

    Error text should be defined in
    `hyperglass.configuration.params.messages` and associated with the
    exception class at start time.
    """

    _level = "warning"
    _message_template = "Something went wrong."

    def __init_subclass__(
        cls, *, template: Optional[str] = None, level: Optional[ErrorLevel] = None
    ) -> None:
        """Override error attributes from subclass."""

        if template is not None:
            cls._message_template = template
        if level is not None:
            cls._level = level

    def __init__(self, **kwargs: str) -> None:
        """Format error message with keyword arguments."""
        if "error" in kwargs:
            error = kwargs.pop("error")
            error = self._safe_format(str(error), **kwargs)
            kwargs["error"] = error
        self._message = self._safe_format(self._message_template, **kwargs)
        self._keywords = list(kwargs.values())
        super().__init__(message=self._message, level=self._level, keywords=self._keywords)

    def handle_error(self, error: Any) -> None:
        """Add details to the error template, if provided."""

        if error is not None:
            self._message_template = self._message_template + " ({error})"


class PrivateHyperglassError(HyperglassError):
    """Base exception class for internal system errors.

    Error text is dynamic based on the exception being caught.
    """

    _level = "warning"

    def __init_subclass__(cls, *, level: Optional[ErrorLevel] = None) -> None:
        """Override error attributes from subclass."""
        if level is not None:
            cls._level = level

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Format error message with keyword arguments."""
        if "error" in kwargs:
            error = kwargs.pop("error")
            error = self._safe_format(str(error), **kwargs)
            kwargs["error"] = error
        self._message = self._safe_format(message, **kwargs)
        self._keywords = list(kwargs.values())
        super().__init__(message=self._message, level=self._level, keywords=self._keywords)
