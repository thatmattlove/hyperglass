# Standard Library Imports
import re
from ipaddress import ip_network

# Project Imports
from hyperglass.configuration import params
from hyperglass.exceptions import InputInvalid


def validate_ip(value, query_type):
    """Ensure input IP address is both valid and not within restricted allocations.

    Arguments:
        value {str} -- Unvalidated IP Address
    Raises:
        ValueError: Raised if input IP address is not an IP address.
        ValueError: Raised if IP address is valid, but is within a restricted range.
    Returns:
        Union[IPv4Address, IPv6Address] -- Validated IP address object
    """
    query_type_params = getattr(params.queries, query_type)
    try:

        # Attempt to use IP object factory to create an IP address object
        valid_ip = ip_network(value)

    except ValueError:
        raise InputInvalid(
            params.messages.invalid_input,
            target=value,
            query_type=query_type_params.display_name,
        )

    """
    Test the valid IP address to determine if it is:
      - Unspecified (See RFC5735, RFC2373)
      - Loopback (See RFC5735, RFC2373)
      - Otherwise IETF Reserved
    ...and returns an error if so.
    """

    if valid_ip.is_reserved or valid_ip.is_unspecified or valid_ip.is_loopback:
        raise InputInvalid(
            params.messages.invalid_input,
            target=value,
            query_type=query_type_params.display_name,
        )

    """
    If the valid IP is a host and not a network, return the
    IPv4Address/IPv6Address object instead of IPv4Network/IPv6Network.
    """
    if valid_ip.num_addresses == 1:
        valid_ip = valid_ip.network_address

    return valid_ip


def validate_community(value, query_type):
    """Validate input communities against configured or default regex pattern."""

    # RFC4360: Extended Communities (New Format)
    if re.match(params.queries.bgp_community.regex.extended_as, value):
        pass

    # RFC4360: Extended Communities (32 Bit Format)
    elif re.match(params.queries.bgp_community.regex.decimal, value):
        pass

    # RFC8092: Large Communities
    elif re.match(params.queries.bgp_community.regex.large, value):
        pass

    else:
        raise InputInvalid(
            params.messages.invalid_input,
            target=value,
            query_type=params.queries.bgp_community.display_name,
        )
    return value


def validate_aspath(value, query_type):
    """Validate input AS_PATH against configured or default regext pattern."""

    mode = params.queries.bgp_aspath.regex.mode
    pattern = getattr(params.queries.bgp_aspath.regex, mode)

    if not re.match(pattern, value):
        raise InputInvalid(
            params.messages.invalid_input,
            target=value,
            query_type=params.queries.bgp_aspath.display_name,
        )

    return value
