"""Validate VRF configuration variables."""

# Standard Library Imports
from ipaddress import IPv4Address
from ipaddress import IPv4Network
from ipaddress import IPv6Address
from ipaddress import IPv6Network
from typing import Dict
from typing import List
from typing import Optional

# Third Party Imports
from pydantic import IPvAnyNetwork
from pydantic import StrictStr
from pydantic import constr
from pydantic import validator

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel


class DeviceVrf4(HyperglassModel):
    """Validation model for IPv4 AFI definitions."""

    vrf_name: StrictStr
    source_address: IPv4Address


class DeviceVrf6(HyperglassModel):
    """Validation model for IPv6 AFI definitions."""

    vrf_name: StrictStr
    source_address: IPv6Address


class Vrf(HyperglassModel):
    """Validation model for per VRF/afi config in devices.yaml."""

    name: str
    display_name: str
    ipv4: Optional[DeviceVrf4]
    ipv6: Optional[DeviceVrf6]
    access_list: List[Dict[constr(regex=("allow|deny")), IPvAnyNetwork]] = [
        {"allow": IPv4Network("0.0.0.0/0")},
        {"allow": IPv6Network("::/0")},
    ]

    @validator("ipv4", "ipv6", pre=True, always=True)
    def set_default_vrf_name(cls, value, values):
        """If per-AFI name is undefined, set it to the global VRF name.

        Returns:
            {str} -- VRF Name
        """
        if isinstance(value, DefaultVrf) and value.vrf_name is None:
            value["vrf_name"] = values["name"]
        elif isinstance(value, Dict) and value.get("vrf_name") is None:
            value["vrf_name"] = values["name"]
        return value

    @validator("access_list", pre=True)
    def validate_action(cls, value):
        """Transform ACL networks to IPv4Network/IPv6Network objects.

        Returns:
            {object} -- IPv4Network/IPv6Network object
        """
        for li in value:
            for action, network in li.items():
                if isinstance(network, (IPv4Network, IPv6Network)):
                    li[action] = str(network)
        return value


class DefaultVrf(HyperglassModel):
    """Validation model for default routing table VRF."""

    name: StrictStr = "default"
    display_name: StrictStr = "Global"
    access_list: List[Dict[constr(regex=("allow|deny")), IPvAnyNetwork]] = [
        {"allow": IPv4Network("0.0.0.0/0")},
        {"allow": IPv6Network("::/0")},
    ]

    class DefaultVrf4(HyperglassModel):
        """Validation model for IPv4 default routing table VRF definition."""

        vrf_name: StrictStr = "default"
        source_address: IPv4Address

    class DefaultVrf6(HyperglassModel):
        """Validation model for IPv6 default routing table VRF definition."""

        vrf_name: StrictStr = "default"
        source_address: IPv6Address

    ipv4: Optional[DefaultVrf4]
    ipv6: Optional[DefaultVrf6]
