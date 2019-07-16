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
from hyperglass.constants import code


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
    validity = False
    try:
        valid_ip = ipaddress.ip_network(target)
        if valid_ip.is_reserved or valid_ip.is_unspecified or valid_ip.is_loopback:
            raise ValueError
        validity = True
    except (ipaddress.AddressValueError, ValueError):
        logger.debug(f"IP {target} is invalid")
        validity = False
    return validity


def ip_blacklist(target):
    """
    Check blacklist list for prefixes/IPs, return boolean based on list
    membership.
    """
    logger.debug(f"Blacklist Enabled: {params.features.blacklist.enable}")
    membership = False
    if params.features.blacklist.enable:
        target_ver = ipaddress.ip_network(target).version
        user_blacklist = params.features.blacklist.networks
        networks = [
            net
            for net in user_blacklist
            if ipaddress.ip_network(net).version == target_ver
        ]
        logger.debug(
            f"IPv{target_ver} Blacklist Networks: {[str(n) for n in networks]}"
        )
        while not membership:
            for net in networks:
                if ipaddress.ip_network(target).subnet_of(net):
                    membership = True
                    logger.debug(f"Blacklist Match Found for {target} in {net}")
                    break
            break
    return membership


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
    validity = False
    msg = params.messages.not_allowed.format(i=target)
    # If target is a member of the blacklist, return an error.
    if ip_blacklist(target):
        validity = False
        logger.debug("Failed blacklist check")
        return (validity, msg)
    # If enable_max_prefix feature enabled, require that BGP Route
    # queries be smaller than configured size limit.
    if query_type == "bgp_route" and params.features.max_prefix.enable:
        max_length = getattr(params.features.max_prefix, prefix_attr["afi"])
        if prefix_attr["length"] > max_length:
            validity = False
            msg = params.features.max_prefixmessage.format(
                m=max_length, i=prefix_attr["network"]
            )
            logger.debug("Failed max prefix length check")
            return (validity, msg)
    # If device NOS is listed in requires_ipv6_cidr.toml, and query is
    # an IPv6 host address, return an error.
    if (
        query_type == "bgp_route"
        and prefix_attr["version"] == 6
        and device.nos in params.general.requires_ipv6_cidr
        and IPType().is_host(target)
    ):
        msg = params.messages.requires_ipv6_cidr.format(d=device.display_name)
        validity = False
        logger.debug("Failed requires IPv6 CIDR check")
        return (validity, msg)
    # If query type is ping or traceroute, and query target is in CIDR
    # format, return an error.
    if query_type in ("ping", "traceroute") and IPType().is_cidr(target):
        msg = params.messages.directed_cidr.format(q=query_type.capitalize())
        validity = False
        logger.debug("Failed CIDR format for ping/traceroute check")
        return (validity, msg)
    validity = True
    msg = f"{target} is a valid {query_type} query."
    return (validity, msg)


class Validate:
    """
    Accepts raw input and associated device parameters from execute.py
    and validates the input based on specific query type. Returns
    boolean for validity, specific error message, and status code.
    """

    def __init__(self, device):
        """Initialize device parameters and error codes."""
        self.device = device

    def ping(self, target):
        """Ping Query: Input Validation & Error Handling"""
        query_type = "ping"
        logger.debug(f"Validating {query_type} query for target {target}...")
        validity = False
        msg = params.messages.invalid_ip.format(i=target)
        status = code.not_allowed
        # Perform basic validation of an IP address, return error if
        # not a valid IP.
        if not ip_validate(target):
            status = code.invalid
            logger.error(f"{msg}, {status}")
            return (validity, msg, status)
        # Perform further validation of a valid IP address, return an
        # error upon failure.
        valid_query, msg = ip_type_check(query_type, target, self.device)
        if valid_query:
            validity = True
            msg = f"{target} is a valid {query_type} query."
            status = code.valid
            logger.debug(f"{msg}, {status}")
            return (validity, msg, status)
        return (validity, msg, status)

    def traceroute(self, target):
        """Traceroute Query: Input Validation & Error Handling"""
        query_type = "traceroute"
        logger.debug(f"Validating {query_type} query for target {target}...")
        validity = False
        msg = params.messages.invalid_ip.format(i=target)
        status = code.not_allowed
        # Perform basic validation of an IP address, return error if
        # not a valid IP.
        if not ip_validate(target):
            status = code.invalid
            logger.error(f"{msg}, {status}")
            return (validity, msg, status)
        # Perform further validation of a valid IP address, return an
        # error upon failure.
        valid_query, msg = ip_type_check(query_type, target, self.device)
        if valid_query:
            validity = True
            msg = f"{target} is a valid {query_type} query."
            status = code.valid
            logger.debug(f"{msg}, {status}")
            return (validity, msg, status)
        return (validity, msg, status)

    def bgp_route(self, target):
        """BGP Route Query: Input Validation & Error Handling"""
        query_type = "bgp_route"
        logger.debug(f"Validating {query_type} query for target {target}...")
        validity = False
        msg = params.messages.invalid_ip.format(i=target)
        status = code.not_allowed
        # Perform basic validation of an IP address, return error if not
        # a valid IP.
        if not ip_validate(target):
            status = code.invalid
            logger.error(f"{msg}, {status}")
            return (validity, msg, status)
        # Perform further validation of a valid IP address, return an
        # error upon failure.
        valid_query, msg = ip_type_check(query_type, target, self.device)
        if valid_query:
            validity = True
            msg = f"{target} is a valid {query_type} query."
            status = code.valid
            logger.debug(f"{msg}, {status}")
            return (validity, msg, status)
        return (validity, msg, status)

    @staticmethod
    def bgp_community(target):
        """BGP Community Query: Input Validation & Error Handling"""
        query_type = "bgp_community"
        logger.debug(f"Validating {query_type} query for target {target}...")
        validity = False
        msg = params.messages.invalid_dual.format(i=target, qt="BGP Community")
        status = code.invalid
        # Validate input communities against configured or default regex
        # pattern.
        # Extended Communities, new-format
        if re.match(params.features.bgp_community.regex.extended_as, target):
            validity = True
            msg = f"{target} matched extended AS format community."
            status = code.valid
        # Extended Communities, 32 bit format
        elif re.match(params.features.bgp_community.regex.decimal, target):
            validity = True
            msg = f"{target} matched decimal format community."
            status = code.valid
        # RFC 8092 Large Community Support
        elif re.match(params.features.bgp_community.regex.large, target):
            validity = True
            msg = f"{target} matched large community."
            status = code.valid
        logger.debug(f"{msg}, {status}")
        return (validity, msg, status)

    @staticmethod
    def bgp_aspath(target):
        """BGP AS Path Query: Input Validation & Error Handling"""
        query_type = "bgp_aspath"
        logger.debug(f"Validating {query_type} query for target {target}...")
        validity = False
        msg = params.messages.invalid_dual.format(i=target, qt="AS Path")
        status = code.invalid
        # Validate input AS_PATH regex pattern against configured or
        # default regex pattern.
        mode = params.features.bgp_aspath.regex.mode
        pattern = getattr(params.features.bgp_aspath.regex, mode)
        if re.match(pattern, target):
            validity = True
            msg = f"{target} matched AS_PATH regex."
            status = code.valid
        logger.debug(f"{msg}, {status}")
        return (validity, msg, status)
