"""Validate logging configuration."""

# Standard Library
import base64
from ast import literal_eval
from typing import Dict, Union, Optional
from pathlib import Path

# Third Party
from pydantic import (
    ByteSize,
    SecretStr,
    StrictInt,
    StrictStr,
    AnyHttpUrl,
    StrictBool,
    StrictFloat,
    DirectoryPath,
    constr,
    validator,
)

# Project
from hyperglass.models import HyperglassModel, HyperglassModelExtra
from hyperglass.constants import __version__


class Syslog(HyperglassModel):
    """Validation model for syslog configuration."""

    enable: StrictBool = True
    host: StrictStr
    port: StrictInt = 514


class HttpAuth(HyperglassModel):
    """HTTP hook authentication parameters."""

    mode: constr(regex=r"(basic|api_key)") = "basic"
    username: Optional[StrictStr]
    password: SecretStr

    def api_key(self, header_name="X-API-Key"):
        """Represent authentication as an API key header."""
        return {header_name: self.password.get_secret_value()}

    def basic(self):
        """Represent HTTP basic authentication."""
        return (self.username, self.password.get_secret_value())


class Http(HyperglassModelExtra):
    """HTTP logging parameters."""

    enable: StrictBool = True
    provider: constr(regex=r"(slack|generic)") = "generic"
    host: AnyHttpUrl
    authentication: Optional[HttpAuth]
    headers: Dict[StrictStr, Union[StrictStr, StrictInt, StrictBool, None]] = {}
    params: Dict[StrictStr, Union[StrictStr, StrictInt, StrictBool, None]] = {}
    verify_ssl: StrictBool = True
    timeout: Union[StrictFloat, StrictInt] = 5.0

    @validator("headers", "params")
    def stringify_headers_params(cls, value):
        """Ensure headers and URL parameters are strings."""
        for k, v in value.items():
            if not isinstance(v, str):
                value[k] = str(v)
        return value

    def __init__(self, **kwargs):
        """Initialize model, add obfuscated connection details as attribute."""
        super().__init__(**kwargs)
        dumped = {
            "headers": self.headers,
            "params": self.params,
            "verify": self.verify_ssl,
            "timeout": self.timeout,
        }
        dumped["headers"].update({"user-agent": f"hyperglass/{__version__}"})

        if self.authentication is not None:
            if self.authentication.mode == "api_key":
                dumped["headers"].update(self.authentication.api_key())
            else:
                dumped["auth"] = self.authentication.basic()

        self._obscured_params = base64.encodestring(str(dumped).encode())

    def decoded(self):
        """Decode connection details."""
        return literal_eval(base64.decodestring(self._obscured_params).decode())


class Logging(HyperglassModel):
    """Validation model for logging configuration."""

    directory: DirectoryPath = Path("/tmp")  # noqa: S108
    format: constr(regex=r"(text|json)") = "text"
    max_size: ByteSize = "50MB"
    syslog: Optional[Syslog]
    http: Optional[Http]
