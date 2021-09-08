"""Validate SSH proxy configuration variables."""

# Standard Library
from typing import Union
from ipaddress import IPv4Address, IPv6Address

# Third Party
from pydantic import StrictInt, StrictStr, validator

# Project
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
    nos: StrictStr = "linux_ssh"

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

    @validator("nos")
    def supported_nos(cls, value, values):
        """Verify NOS is supported by hyperglass."""

        if not value == "linux_ssh":
            raise UnsupportedDevice(
                "Proxy '{p}' uses NOS '{n}', which is currently unsupported.",
                p=values["name"],
                n=value,
            )
        return value
