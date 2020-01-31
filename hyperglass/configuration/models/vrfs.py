"""Validate VRF configuration variables."""

# Standard Library Imports
from ipaddress import IPv4Address
from ipaddress import IPv4Network
from ipaddress import IPv6Address
from ipaddress import IPv6Network
from typing import List
from typing import Optional

# Third Party Imports
from pydantic import FilePath
from pydantic import StrictBool
from pydantic import StrictStr
from pydantic import conint
from pydantic import constr
from pydantic import root_validator
from pydantic import validator

# Project Imports
from hyperglass.configuration.models._utils import HyperglassModel
from hyperglass.configuration.models._utils import HyperglassModelExtra


class AccessList4(HyperglassModel):
    """Validation model for IPv4 access-lists."""

    network: IPv4Network = "0.0.0.0/0"
    action: constr(regex="permit|deny") = "permit"
    ge: conint(ge=0, le=32) = 0
    le: conint(ge=0, le=32) = 32

    @validator("ge")
    def validate_model(cls, value, values):
        """Ensure ge is at least the size of the input prefix.

        Arguments:
            value {int} -- Initial ge value
            values {dict} -- Other post-validation fields

        Returns:
            {int} -- Validated ge value
        """
        net_len = values["network"].prefixlen
        if net_len > value:
            value = net_len
        return value


class AccessList6(HyperglassModel):
    """Validation model for IPv6 access-lists."""

    network: IPv6Network = "::/0"
    action: constr(regex=r"permit|deny") = "permit"
    ge: conint(ge=0, le=128) = 0
    le: conint(ge=0, le=128) = 128

    @validator("ge")
    def validate_model(cls, value, values):
        """Ensure ge is at least the size of the input prefix.

        Arguments:
            value {int} -- Initial ge value
            values {dict} -- Other post-validation fields

        Returns:
            {int} -- Validated ge value
        """
        net_len = values["network"].prefixlen
        if net_len > value:
            value = net_len
        return value


class InfoConfigParams(HyperglassModelExtra):
    """Validation model for per-help params."""

    title: Optional[StrictStr]


class InfoConfig(HyperglassModel):
    """Validation model for help configuration."""

    enable: StrictBool = True
    file: Optional[FilePath]
    params: InfoConfigParams = InfoConfigParams()


class Info(HyperglassModel):
    """Validation model for per-VRF, per-Command help."""

    bgp_aspath: InfoConfig = InfoConfig()
    bgp_community: InfoConfig = InfoConfig()
    bgp_route: InfoConfig = InfoConfig()
    ping: InfoConfig = InfoConfig()
    traceroute: InfoConfig = InfoConfig()


class DeviceVrf4(HyperglassModelExtra):
    """Validation model for IPv4 AFI definitions."""

    source_address: IPv4Address
    access_list: List[AccessList4] = [AccessList4()]


class DeviceVrf6(HyperglassModelExtra):
    """Validation model for IPv6 AFI definitions."""

    source_address: IPv6Address
    access_list: List[AccessList6] = [AccessList6()]


class Vrf(HyperglassModel):
    """Validation model for per VRF/afi config in devices.yaml."""

    name: StrictStr
    display_name: StrictStr
    info: Info = Info()
    ipv4: Optional[DeviceVrf4]
    ipv6: Optional[DeviceVrf6]

    @root_validator
    def set_dynamic(cls, values):
        """Set dynamic attributes before VRF initialization.

        Arguments:
            values {dict} -- Post-validation VRF attributes

        Returns:
            {dict} -- VRF with new attributes set
        """
        if values["name"] == "default":
            protocol4 = "ipv4_default"
            protocol6 = "ipv6_default"

        else:
            protocol4 = "ipv4_vpn"
            protocol6 = "ipv6_vpn"

        if values.get("ipv4") is not None:
            values["ipv4"].protocol = protocol4
            values["ipv4"].version = 4

        if values.get("ipv6") is not None:
            values["ipv6"].protocol = protocol6
            values["ipv6"].version = 6

        return values

    def __getitem__(self, i):
        """Access the VRF's AFI by IP protocol number.

        Arguments:
            i {int} -- IP Protocol number (4|6)

        Raises:
            AttributeError: Raised if passed number is not 4 or 6.

        Returns:
            {object} -- AFI object
        """
        if i not in (4, 6):
            raise AttributeError(f"Must be 4 or 6, got '{i}")

        return getattr(self, f"ipv{i}")

    def __hash__(self):
        """Make VRF object hashable so the object can be deduplicated with set().

        Returns:
            {int} -- Hash of VRF name
        """
        return hash((self.name,))

    def __eq__(self, other):
        """Make VRF object comparable so the object can be deduplicated with set().

        Arguments:
            other {object} -- Object to compare

        Returns:
            {bool} -- True if comparison attributes are the same value
        """
        result = False
        if isinstance(other, HyperglassModel):
            result = self.name == other.name
        return result


class DefaultVrf(HyperglassModel):
    """Validation model for default routing table VRF."""

    name: constr(regex="default") = "default"
    display_name: StrictStr = "Global"
    info: Info = Info()

    class DefaultVrf4(HyperglassModel):
        """Validation model for IPv4 default routing table VRF definition."""

        source_address: IPv4Address
        access_list: List[AccessList4] = [AccessList4()]

    class DefaultVrf6(HyperglassModel):
        """Validation model for IPv6 default routing table VRF definition."""

        source_address: IPv6Address
        access_list: List[AccessList6] = [AccessList6()]

    ipv4: Optional[DefaultVrf4]
    ipv6: Optional[DefaultVrf6]
