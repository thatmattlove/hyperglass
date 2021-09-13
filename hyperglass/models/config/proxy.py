"""Validate SSH proxy configuration variables."""

# Standard Library
from typing import Union, Any, Dict
from ipaddress import IPv4Address, IPv6Address

# Third Party
from pydantic import StrictInt, StrictStr, validator, Field

# Project
from hyperglass.log import log
from hyperglass.util import resolve_hostname
from hyperglass.exceptions.private import ConfigError, UnsupportedDevice

# Local
from ..main import HyperglassModel
from .credential import Credential


class Proxy(HyperglassModel):
    """Validation model for per-proxy config in devices.yaml."""

    name: StrictStr
    address: Union[IPv4Address, IPv6Address, StrictStr]
    port: StrictInt = 22
    credential: Credential
    type: StrictStr = Field("linux_ssh", alias="nos")

    @property
    def _target(self):
        return str(self.address)

    @validator("address")
    def validate_address(cls, value, values):
        """Ensure a hostname is resolvable."""

        if not isinstance(value, (IPv4Address, IPv6Address)):
            if not any(resolve_hostname(value)):
                raise ConfigError(
                    "Device '{d}' has an address of '{a}', which is not resolvable.",
                    d=values["name"],
                    a=value,
                )
        return value

    @validator("type", pre=True, always=True)
    def validate_type(cls: "Proxy", value: Any, values: Dict[str, Any]) -> str:
        """Validate device type."""
        legacy = values.pop("nos", None)
        if legacy is not None and value is None:
            log.warning(
                "The 'nos' field on proxy '{}' has been deprecated and will be removed in a future release. Use the 'type' field moving forward.",
                values.get("name", "Unknown"),
            )
            return legacy
        if value is not None:
            if value != "linux_ssh":
                raise UnsupportedDevice(
                    "Proxy '{p}' uses type '{t}', which is currently unsupported.",
                    p=values["name"],
                    t=value,
                )
            return value
        raise ValueError("type is missing")
