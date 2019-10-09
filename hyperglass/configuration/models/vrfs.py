"""
Defines models for VRF config variables.

Imports config variables and overrides default class attributes.

Validates input for overridden parameters.
"""
# Standard Library Imports
from ipaddress import IPv4Address
from ipaddress import IPv4Network
from ipaddress import IPv6Address
from ipaddress import IPv6Network
from typing import Dict
from typing import List
from typing import Union

# Third Party Imports
from pydantic import IPvAnyNetwork
from pydantic import constr
from pydantic import validator

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel
from hyperglass.exceptions import ConfigError


class DeviceVrf4(HyperglassModel):
    """Model for AFI definitions"""

    afi_name: str = "ipv4"
    vrf_name: str
    source_address: IPv4Address

    @validator("source_address")
    def check_ip_type(cls, value, values):
        if value is not None and isinstance(value, IPv4Address):
            if value.is_loopback:
                raise ConfigError(
                    (
                        "The default routing table with source IPs must be defined. "
                        "VRF: {vrf}, Source Address: {value}"
                    ),
                    vrf=values["vrf_name"],
                    value=value,
                )
        return value


class DeviceVrf6(HyperglassModel):
    """Model for AFI definitions"""

    afi_name: str = "ipv6"
    vrf_name: str
    source_address: IPv6Address

    @validator("source_address")
    def check_ip_type(cls, value, values):
        if value is not None and isinstance(value, IPv4Address):
            if value.is_loopback:
                raise ConfigError(
                    (
                        "The default routing table with source IPs must be defined. "
                        "VRF: {vrf}, Source Address: {value}"
                    ),
                    vrf=values["vrf_name"],
                    value=value,
                )
        return value


class Vrf(HyperglassModel):
    """Model for per VRF/afi config in devices.yaml"""

    name: str
    display_name: str
    ipv4: Union[DeviceVrf4, None]
    ipv6: Union[DeviceVrf6, None]
    access_list: List[Dict[constr(regex=("allow|deny")), IPvAnyNetwork]] = [
        {"allow": IPv4Network("0.0.0.0/0")},
        {"allow": IPv6Network("::/0")},
    ]

    @validator("ipv4", "ipv6", pre=True, whole=True)
    def set_default_vrf_name(cls, value, values):
        if value is not None and value.get("vrf_name") is None:
            value["vrf_name"] = values["name"]
        return value

    @validator("access_list", pre=True, whole=True, always=True)
    def validate_action(cls, value):
        for li in value:
            for action, network in li.items():
                if isinstance(network, (IPv4Network, IPv6Network)):
                    li[action] = str(network)
        return value


class DefaultVrf(HyperglassModel):

    name: str = "default"
    display_name: str = "Global"
    access_list = [{"allow": IPv4Network("0.0.0.0/0")}, {"allow": IPv6Network("::/0")}]

    class DefaultVrf4(HyperglassModel):
        afi_name: str = "ipv4"
        vrf_name: str = "default"
        source_address: IPv4Address = IPv4Address("127.0.0.1")

    class DefaultVrf6(HyperglassModel):
        afi_name: str = "ipv4"
        vrf_name: str = "default"
        source_address: IPv6Address = IPv6Address("::1")

    ipv4: DefaultVrf4 = DefaultVrf4()
    ipv6: DefaultVrf6 = DefaultVrf6()
