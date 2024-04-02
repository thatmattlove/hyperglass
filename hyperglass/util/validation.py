"""Validation Utilities."""

# Standard Library
import typing as t

# Third Party
from netmiko.ssh_dispatcher import CLASS_MAPPER  # type: ignore

# Project
from hyperglass.constants import DRIVER_MAP

if t.TYPE_CHECKING:
    # Standard Library
    from ipaddress import IPv4Address, IPv6Address


def validate_platform(_type: str) -> t.Tuple[bool, t.Union[None, str]]:
    """Validate device type is supported."""

    all_device_types = {*DRIVER_MAP.keys(), *CLASS_MAPPER.keys()}

    result = (False, None)

    if _type in all_device_types:
        result = (True, DRIVER_MAP.get(_type, "netmiko"))

    return result


def get_driver(_type: str, driver: t.Optional[str]) -> str:
    """Determine the appropriate driver for a device."""

    if driver is None:
        # If no driver is set, use the driver map with netmiko as
        # fallback.
        return DRIVER_MAP.get(_type, "netmiko")

    all_drivers = {*DRIVER_MAP.values(), "netmiko"}

    if driver in all_drivers:
        # If a driver is set and it is valid, allow it.
        return driver

    # Otherwise, fail validation.
    raise ValueError("{} is not a supported driver.".format(driver))


def resolve_hostname(
    hostname: str,
) -> t.Generator[t.Union["IPv4Address", "IPv6Address"], None, None]:
    """Resolve a hostname via DNS/hostfile."""
    # Standard Library
    from socket import gaierror, getaddrinfo
    from ipaddress import ip_address

    # Project
    from hyperglass.log import log

    log.bind(hostname=hostname).debug("Ensuring hostname is resolvable")

    ip4 = None
    ip6 = None
    try:
        res = getaddrinfo(hostname, None)
        for sock in res:
            if sock[0].value == 2 and ip4 is None:
                ip4 = ip_address(sock[4][0])
            elif sock[0].value in (10, 30) and ip6 is None:
                ip6 = ip_address(sock[4][0])
    except (gaierror, ValueError, IndexError) as err:
        log.debug(str(err))
        pass

    yield ip4
    yield ip6
