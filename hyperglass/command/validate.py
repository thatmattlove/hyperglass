# https://github.com/checktheroads/hyperglass
"""
Accepts raw input data from execute.py, passes it through specific filters based on query type, \
returns validity boolean and specific error message.
"""
# Standard Imports
import re
import inspect
import logging

# Module Imports
import logzero
from logzero import logger
from netaddr.core import AddrFormatError
from netaddr import IPNetwork, IPAddress, IPSet  # pylint: disable=unused-import

# Dear PyLint, the netaddr library is a special snowflake. You might not see `IPAddress` get used, \
# but when you use something like `IPNetwork("192.0.2.1/24").ip`, the returned value is \
# IPAddress("192.0.2.1"), so I do actually need this import. <3, -ML

# Project Imports
from hyperglass import configuration

# Configuration Imports
config = configuration.params()

# Logzero Configuration
if configuration.debug_state():
    logzero.loglevel(logging.DEBUG)
else:
    logzero.loglevel(logging.INFO)


class IPType:
    """
    Passes input through IPv4/IPv6 regex patterns to determine if input is formatted as a host \
    (e.g. 192.0.2.1), or as CIDR (e.g. 192.0.2.0/24). is_host() and is_cidr() return a boolean.
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
            r"(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|"
            r"([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA\-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}"
            r"(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:("
            r"(:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::"
            r"(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25"
            r"[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]"
            r"|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))?$"
        )
        self.ipv6_cidr = (
            r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|"
            r"([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]"
            r"{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}"
            r":){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}"
            r"|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:"
            r"(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|"
            r"(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])"
            r"|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25"
            r"[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\/((1(1[0-9]|2[0-8]))|([0-9][0-9])|([0-9]"
            r"))?$"
        )

    def is_host(self, target):
        """Tests input to see if formatted as host"""
        ip_version = IPNetwork(target).ip.version
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
        ip_version = IPNetwork(target).ip.version
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
        valid_ip = IPNetwork(target).ip
        if (
            valid_ip.is_reserved()
            or valid_ip.is_netmask()
            or valid_ip.is_hostmask()
            or valid_ip.is_loopback()
        ):
            validity = False
            logger.debug(f"IP {valid_ip} is invalid")
        if valid_ip.is_unicast():
            validity = True
            logger.debug(f"IP {valid_ip} is valid")
    except AddrFormatError:
        logger.debug(f"IP {target} is invalid")
        validity = False
    return validity


def ip_blacklist(target):
    """Check blacklist list for prefixes/IPs, return boolean based on list membership"""
    blacklist = IPSet(configuration.blacklist())
    logger.debug(f"Blacklist: {blacklist}")
    membership = False
    if target in blacklist:
        membership = True
    return membership


def ip_attributes(target):
    """Construct dictionary of validated IP attributes for repeated use"""
    network = IPNetwork(target)
    addr = network.ip
    ip_version = addr.version
    afi = f"ipv{ip_version}"
    afi_pretty = f"IPv{ip_version}"
    length = network.prefixlen
    valid_attributes = {
        "prefix": target,
        "network": network,
        "version": ip_version,
        "length": length,
        "afi": afi,
        "afi_pretty": afi_pretty,
    }
    return valid_attributes


def ip_type_check(query_type, target, device):
    """Checks multiple IP address related validation parameters"""
    prefix_attr = ip_attributes(target)
    logger.debug(f"IP Attributes:\n{prefix_attr}")
    requires_ipv6_cidr = configuration.requires_ipv6_cidr(device["type"])
    validity = False
    msg = config["messages"]["not_allowed"].format(i=target)
    # If target is a member of the blacklist, return an error.
    if ip_blacklist(target):
        validity = False
        logger.debug(f"Failed blacklist check")
        return (validity, msg)
    # If enable_max_prefix feature enabled, require that BGP Route queries be smaller than\
    # configured size limit.
    if query_type == "bgp_route" and config["features"]["max_prefix"]["enable"]:
        max_length = config["features"]["max_prefix"][prefix_attr["afi"]]
        if prefix_attr["length"] > max_length:
            validity = False
            msg = config["features"]["max_prefix"]["message"].format(
                m=max_length, i=prefix_attr["network"]
            )
            logger.debug(f"Failed max prefix length check")
            return (validity, msg)
    # If device NOS is listed in requires_ipv6_cidr.toml, and query is an IPv6 host address, \
    # return an error.
    if (
        query_type == "bgp_route"
        and prefix_attr["version"] == 6
        and requires_ipv6_cidr
        and IPType().is_host(target)
    ):
        msg = config["messages"]["requires_ipv6_cidr"].format(d=device["display_name"])
        validity = False
        logger.debug(f"Failed requires IPv6 CIDR check")
        return (validity, msg)
    # If query type is ping or traceroute, and query target is in CIDR format, return an error.
    if query_type in ["ping", "traceroute"] and IPType().is_cidr(target):
        msg = config["messages"]["directed_cidr"].format(q=query_type.capitalize())
        validity = False
        logger.debug(f"Failed CIDR format for ping/traceroute check")
        return (validity, msg)
    validity = True
    msg = f"{target} is a valid {query_type} query."
    return (validity, msg)


def current_function():
    """Returns name of current function for easy initialization & calling."""
    this_function = inspect.stack()[1][3]
    return this_function


class Validate:
    """Accepts raw input and associated device parameters from execute.py and validates the input \
    based on specific query type. Returns boolean for validity, specific error message, and status \
    code."""

    def __init__(self, device):
        """Initialize device parameters and error codes."""
        self.device = device
        self.codes = configuration.codes()

    def ping(self, target):
        """Ping Query: Input Validation & Error Handling"""
        query_type = current_function()
        logger.debug(f"Validating {query_type} query for target {target}...")
        validity = False
        msg = config["messages"]["invalid_ip"].format(i=target)
        status = self.codes["warning"]
        # Perform basic validation of an IP address, return error if not a valid IP.
        if not ip_validate(target):
            status = self.codes["danger"]
            logger.error(f"{msg}, {status}")
            return (validity, msg, status)
        # Perform further validation of a valid IP address, return an error upon failure.
        valid_query, msg = ip_type_check(query_type, target, self.device)
        if valid_query:
            validity = True
            msg = f"{target} is a valid {query_type} query."
            status = self.codes["success"]
            logger.debug(f"{msg}, {status}")
            return (validity, msg, status)
        return (validity, msg, status)

    def traceroute(self, target):
        """Traceroute Query: Input Validation & Error Handling"""
        query_type = current_function()
        logger.debug(f"Validating {query_type} query for target {target}...")
        validity = False
        msg = config["messages"]["invalid_ip"].format(i=target)
        status = self.codes["warning"]
        # Perform basic validation of an IP address, return error if not a valid IP.
        if not ip_validate(target):
            status = self.codes["danger"]
            logger.error(f"{msg}, {status}")
            return (validity, msg, status)
        # Perform further validation of a valid IP address, return an error upon failure.
        valid_query, msg = ip_type_check(query_type, target, self.device)
        if valid_query:
            validity = True
            msg = f"{target} is a valid {query_type} query."
            status = self.codes["success"]
            logger.debug(f"{msg}, {status}")
            return (validity, msg, status)
        return (validity, msg, status)

    def bgp_route(self, target):
        """BGP Route Query: Input Validation & Error Handling"""
        query_type = current_function()
        logger.debug(f"Validating {query_type} query for target {target}...")
        validity = False
        msg = config["messages"]["invalid_ip"].format(i=target)
        status = self.codes["warning"]
        # Perform basic validation of an IP address, return error if not a valid IP.
        if not ip_validate(target):
            status = self.codes["danger"]
            logger.error(f"{msg}, {status}")
            return (validity, msg, status)
        # Perform further validation of a valid IP address, return an error upon failure.
        valid_query, msg = ip_type_check(query_type, target, self.device)
        if valid_query:
            validity = True
            msg = f"{target} is a valid {query_type} query."
            status = self.codes["success"]
            logger.debug(f"{msg}, {status}")
            return (validity, msg, status)
        return (validity, msg, status)

    def bgp_community(self, target):
        """BGP Community Query: Input Validation & Error Handling"""
        query_type = current_function()
        logger.debug(f"Validating {query_type} query for target {target}...")
        validity = False
        msg = config["messages"]["invalid_dual"].format(i=target, qt="BGP Community")
        status = self.codes["danger"]
        # Validate input communities against configured or default regex pattern
        # Extended Communities, new-format
        if re.match(config["features"][query_type]["regex"]["extended_as"], target):
            validity = True
            msg = f"{target} matched extended AS format community."
            status = self.codes["success"]
        # Extended Communities, 32 bit format
        if re.match(config["features"][query_type]["regex"]["decimal"], target):
            validity = True
            msg = f"{target} matched decimal format community."
            status = self.codes["success"]
        # RFC 8092 Large Community Support
        if re.match(config["features"][query_type]["regex"]["large"], target):
            validity = True
            msg = f"{target} matched large community."
            status = self.codes["success"]
        if not validity:
            logger.error(f"{msg}, {status}")
        logger.debug(f"{msg}, {status}")
        return (validity, msg, status)

    def bgp_aspath(self, target):
        """BGP AS Path Query: Input Validation & Error Handling"""
        query_type = current_function()
        logger.debug(f"Validating {query_type} query for target {target}...")
        validity = False
        msg = config["messages"]["invalid_dual"].format(i=target, qt="AS Path")
        status = self.codes["danger"]
        # Validate input AS_PATH regex pattern against configured or default regex pattern
        if re.match(config["features"][query_type]["regex"]["pattern"], target):
            validity = True
            msg = f"{target} matched AS_PATH regex."
            status = self.codes["success"]
        if not validity:
            logger.error(f"{msg}, {status}")
        logger.debug(f"{msg}, {status}")
        return (validity, msg, status)
