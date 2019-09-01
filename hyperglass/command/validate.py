"""
Accepts raw input data from execute.py, passes it through specific
filters based on query type, returns validity boolean and specific
error message.
"""
# Standard Library Imports
import ipaddress
import re

# Third Party Imports
from logzero import logger

# Project Imports
from hyperglass.configuration import logzero_config  # noqa: F401
from hyperglass.configuration import params
from hyperglass.exceptions import InputInvalid, InputNotAllowed


class IPType:
    """
    Passes input through IPv4/IPv6 regex patterns to determine if input
    is formatted as a host (e.g. 192.0.2.1), or as CIDR
    (e.g. 192.0.2.0/24). is_host() and is_cidr() return a boolean.
    """

    def __init__(self):
        self.ipv4_host = (
            r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4]"
            r"[0-9]|[01]?[0-9][0-9]?)?$"
        )
        self.ipv4_cidr = (
            r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4]"
            r"[0-9]|[01]?[0-9][0-9]?)\/(3[0-2]|2[0-9]|1[0-9]|[0-9])?$"
        )
        self.ipv6_host = (
            r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:)"
            r"{1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}"
            r"(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}"
            r"|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA\-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:)"
            r"{1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})"
            r"|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]"
            r"{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]"
            r")\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:)"
            r"{1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|"
            r"1{0,1}[0-9]){0,1}[0-9]))?$"
        )
        self.ipv6_cidr = (
            r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|"
            r"([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:"
            r"[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|"
            r"([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}"
            r"(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:("
            r"(:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}"
            r"|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.)"
            r"{3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:(("
            r"25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}"
            r"[0-9]){0,1}[0-9]))\/((1(1[0-9]|2[0-8]))|([0-9][0-9])|([0-9]))?$"
        )

    def is_host(self, target):
        """Tests input to see if formatted as host"""
        ip_version = ipaddress.ip_network(target).version
        state = False
        if ip_version == 4 and re.match(self.ipv4_host, target):
            logger.debug(f"{target} is an IPv{ip_version} host.")
            state = True
        if ip_version == 6 and re.match(self.ipv6_host, target):
            logger.debug(f"{target} is an IPv{ip_version} host.")
            state = True
        return state

    def is_cidr(self, target):
        """Tests input to see if formatted as CIDR"""
        ip_version = ipaddress.ip_network(target).version
        state = False
        if ip_version == 4 and re.match(self.ipv4_cidr, target):
            state = True
        if ip_version == 6 and re.match(self.ipv6_cidr, target):
            state = True
        return state


def ip_validate(target):
    """Validates if input is a valid IP address"""
    try:
        valid_ip = ipaddress.ip_network(target)
        if valid_ip.is_reserved or valid_ip.is_unspecified or valid_ip.is_loopback:
            _exception = ValueError(params.messages.invalid_input)
            _exception.details = {}
            raise _exception
    except (ipaddress.AddressValueError, ValueError) as ip_error:
        logger.debug(f"IP {target} is invalid")
        _exception = ValueError(ip_error)
        _exception.details = {}
        raise _exception
    return valid_ip


def ip_blacklist(target):
    """
    Check blacklist list for prefixes/IPs, return boolean based on list
    membership.
    """
    logger.debug(f"Blacklist Enabled: {params.features.blacklist.enable}")
    target = ipaddress.ip_network(target)
    if params.features.blacklist.enable:
        target_ver = target.version
        user_blacklist = params.features.blacklist.networks
        networks = [
            net
            for net in user_blacklist
            if ipaddress.ip_network(net).version == target_ver
        ]
        logger.debug(
            f"IPv{target_ver} Blacklist Networks: {[str(net) for net in networks]}"
        )
        for net in networks:
            blacklist_net = ipaddress.ip_network(net)
            if (
                blacklist_net.network_address <= target.network_address
                and blacklist_net.broadcast_address >= target.broadcast_address
            ):
                logger.debug(f"Blacklist Match Found for {target} in {str(net)}")
                _exception = ValueError(params.messages.blacklist)
                _exception.details = {"blacklisted_net": str(net)}
                raise _exception
    return target


def ip_attributes(target):
    """
    Construct dictionary of validated IP attributes for repeated use.
    """
    network = ipaddress.ip_network(target)
    addr = network.network_address
    ip_version = addr.version
    afi = f"ipv{ip_version}"
    afi_pretty = f"IPv{ip_version}"
    length = network.prefixlen
    return {
        "prefix": target,
        "network": network,
        "version": ip_version,
        "length": length,
        "afi": afi,
        "afi_pretty": afi_pretty,
    }


def ip_type_check(query_type, target, device):
    """Checks multiple IP address related validation parameters"""
    prefix_attr = ip_attributes(target)
    logger.debug(f"IP Attributes:\n{prefix_attr}")

    # If enable_max_prefix feature enabled, require that BGP Route
    # queries be smaller than configured size limit.
    if query_type == "bgp_route" and params.features.max_prefix.enable:
        max_length = getattr(params.features.max_prefix, prefix_attr["afi"])
        if prefix_attr["length"] > max_length:
            logger.debug("Failed max prefix length check")
            _exception = ValueError(params.messages.max_prefix)
            _exception.details = {"max_length": max_length}
            raise _exception

    # If device NOS is listed in requires_ipv6_cidr.toml, and query is
    # an IPv6 host address, return an error.
    if (
        query_type == "bgp_route"
        and prefix_attr["version"] == 6
        and device.nos in params.general.requires_ipv6_cidr
        and IPType().is_host(target)
    ):
        logger.debug("Failed requires IPv6 CIDR check")
        _exception = ValueError(params.messages.requires_ipv6_cidr)
        _exception.details = {"device_name": device.display_name}
        raise _exception

    # If query type is ping or traceroute, and query target is in CIDR
    # format, return an error.
    if query_type in ("ping", "traceroute") and IPType().is_cidr(target):
        logger.debug("Failed CIDR format for ping/traceroute check")
        _exception = ValueError(params.messages.directed_cidr)
        _exception.details = {"query_type": getattr(params.branding.text, query_type)}
        raise _exception
    return target


class Validate:
    """
    Accepts raw input and associated device parameters from execute.py
    and validates the input based on specific query type. Returns
    boolean for validity, specific error message, and status code.
    """

    def __init__(self, device, query_type, target):
        """Initialize device parameters and error codes."""
        self.device = device
        self.query_type = query_type
        self.target = target

    def validate_ip(self):
        """Validates IPv4/IPv6 Input"""
        logger.debug(f"Validating {self.query_type} query for target {self.target}...")

        # Perform basic validation of an IP address, return error if
        # not a valid IP.
        try:
            ip_validate(self.target)
        except ValueError as unformatted_error:
            raise InputInvalid(
                params.messages.invalid_input,
                target=self.target,
                query_type=getattr(params.branding.text, self.query_type),
                **unformatted_error.details,
            )

        # If target is a member of the blacklist, return an error.
        try:
            ip_blacklist(self.target)
        except ValueError as unformatted_error:
            raise InputNotAllowed(
                params.messages.blacklist,
                target=self.target,
                **unformatted_error.details,
            )

        # Perform further validation of a valid IP address, return an
        # error upon failure.
        try:
            ip_type_check(self.query_type, self.target, self.device)
        except ValueError as unformatted_error:
            raise InputNotAllowed(
                str(unformatted_error), target=self.target, **unformatted_error.details
            )

        return self.target

    def validate_dual(self):
        """Validates Dual-Stack Input"""
        logger.debug(f"Validating {self.query_type} query for target {self.target}...")

        if self.query_type == "bgp_community":
            # Validate input communities against configured or default regex
            # pattern.

            # Extended Communities, new-format
            if re.match(params.features.bgp_community.regex.extended_as, self.target):
                pass
            # Extended Communities, 32 bit format
            elif re.match(params.features.bgp_community.regex.decimal, self.target):
                pass
            # RFC 8092 Large Community Support
            elif re.match(params.features.bgp_community.regex.large, self.target):
                pass
            else:
                raise InputInvalid(
                    params.messages.invalid_input,
                    target=self.target,
                    query_type=getattr(params.branding.text, self.query_type),
                )

        elif self.query_type == "bgp_aspath":
            # Validate input AS_PATH regex pattern against configured or
            # default regex pattern.

            mode = params.features.bgp_aspath.regex.mode
            pattern = getattr(params.features.bgp_aspath.regex, mode)
            if re.match(pattern, self.target):
                pass
            else:
                raise InputInvalid(
                    params.messages.invalid_input,
                    target=self.target,
                    query_type=getattr(params.branding.text, self.query_type),
                )
        return self.target

    def validate_query(self):
        if self.query_type in ("bgp_community", "bgp_aspath"):
            return self.validate_dual()
        else:
            return self.validate_ip()
