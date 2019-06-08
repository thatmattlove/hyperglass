# https://github.com/checktheroads/hyperglass
"""
Accepts raw input data from execute.py, passes it through specific filters based on query type, \
returns validity boolean and specific error message.
"""
# Module Imports
import re
import inspect
from logzero import logger
from netaddr.core import AddrFormatError
from netaddr import IPNetwork, IPAddress, IPSet  # pylint: disable=unused-import

# Project Imports
from hyperglass import configuration

# Configuration Imports
config = configuration.general()


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
            state = True
        if ip_version == 6 and re.match(self.ipv6_host, target):
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
        if valid_ip.is_unicast():
            validity = True
    except AddrFormatError:
        validity = False
    return validity


def ip_blacklist(target):
    """Check blacklist list for prefixes/IPs, return boolean based on list membership"""
    blacklist = IPSet(configuration.blacklist())
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


def ip_type_check(cmd, target, device):
    """Checks multiple IP address related validation parameters"""
    prefix_attr = ip_attributes(target)
    requires_ipv6_cidr = configuration.requires_ipv6_cidr(device["type"])
    validity = False
    msg = config["msg_error_notallowed"].format(i=target)
    # If target is a member of the blacklist, return an error.
    if ip_blacklist(target):
        validity = False
        return (validity, msg)
    # If enable_max_prefix feature enabled, require that BGP Route queries be smaller than\
    # configured size limit.
    if cmd == "bgp_route" and config["enable_max_prefix"]:
        max_length = config[f'max_prefix_length_{prefix_attr["afi"]}']
        if prefix_attr["length"] > max_length:
            validity = False
            msg = config["msg_max_prefix"].format(
                m=max_length, i=prefix_attr["network"]
            )
            return (validity, msg)
    # If device NOS is listed in requires_ipv6_cidr.toml, and query is an IPv6 host address, \
    # return an error.
    if (
        cmd == "bgp_route"
        and prefix_attr["version"] == 6
        and requires_ipv6_cidr
        and IPType().is_host(target)
    ):
        msg = config["msg_error_ipv6cidr"].format(d=device["display_name"])
        validity = False
        return (validity, msg)
    # If query type is ping or traceroute, and query target is in CIDR format, return an error.
    if cmd in ["ping", "traceroute"] and IPType().is_cidr(target):
        msg = config["msg_error_directed_cidr"].format(cmd=cmd.capitalize())
        validity = False
        return (validity, msg)
    validity = True
    msg = f"{target} is a valid {cmd} query."
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
        cmd = current_function()
        validity = False
        msg = config["msg_error_invalidip"].format(i=target)
        status = self.codes["warning"]
        # Perform basic validation of an IP address, return error if not a valid IP.
        if not ip_validate(target):
            status = self.codes["danger"]
            logger.error(f"{msg}, {status}")
            return (validity, msg, status)
        # Perform further validation of a valid IP address, return an error upon failure.
        valid_query, msg = ip_type_check(cmd, target, self.device)
        if valid_query:
            validity = True
            msg = f"{target} is a valid {cmd} query."
            status = self.codes["success"]
            return (validity, msg, status)
        return (validity, msg, status)

    def traceroute(self, target):
        """Traceroute Query: Input Validation & Error Handling"""
        cmd = current_function()
        validity = False
        msg = config["msg_error_invalidip"].format(i=target)
        status = self.codes["warning"]
        # Perform basic validation of an IP address, return error if not a valid IP.
        if not ip_validate(target):
            status = self.codes["danger"]
            logger.error(f"{msg}, {status}")
            return (validity, msg, status)
        # Perform further validation of a valid IP address, return an error upon failure.
        valid_query, msg = ip_type_check(cmd, target, self.device)
        if valid_query:
            validity = True
            msg = f"{target} is a valid {cmd} query."
            status = self.codes["success"]
            return (validity, msg, status)
        return (validity, msg, status)

    def bgp_route(self, target):
        """BGP Route Query: Input Validation & Error Handling"""
        cmd = current_function()
        validity = False
        msg = config["msg_error_invalidip"].format(i=target)
        status = self.codes["warning"]
        # Perform basic validation of an IP address, return error if not a valid IP.
        if not ip_validate(target):
            status = self.codes["danger"]
            logger.error(f"{msg}, {status}")
            return (validity, msg, status)
        # Perform further validation of a valid IP address, return an error upon failure.
        valid_query, msg = ip_type_check(cmd, target, self.device)
        if valid_query:
            validity = True
            msg = f"{target} is a valid {cmd} query."
            status = self.codes["success"]
            return (validity, msg, status)
        return (validity, msg, status)

    def bgp_community(self, target):
        """BGP Community Query: Input Validation & Error Handling"""
        validity = False
        msg = config["msg_error_invaliddual"].format(i=target, qt="BGP Community")
        status = self.codes["danger"]
        # Validate input communities against configured or default regex pattern
        # Extended Communities, new-format
        if re.match(config["re_bgp_community_new"], target):
            validity = True
            msg = f"{target} matched new-format community."
            status = self.codes["success"]
        # Extended Communities, 32 bit format
        if re.match(config["re_bgp_community_32bit"], target):
            validity = True
            msg = f"{target} matched 32 bit community."
            status = self.codes["success"]
        # RFC 8092 Large Community Support
        if re.match(config["re_bgp_community_large"], target):
            validity = True
            msg = f"{target} matched large community."
            status = self.codes["success"]
        if not validity:
            logger.error(f"{msg}, {status}")
        return (validity, msg, status)

    def bgp_aspath(self, target):
        """BGP AS Path Query: Input Validation & Error Handling"""
        validity = False
        msg = config["msg_error_invaliddual"].format(i=target, qt="AS Path")
        status = self.codes["danger"]
        # Validate input AS_PATH regex pattern against configured or default regex pattern
        if re.match(config["re_bgp_aspath"], target):
            validity = True
            msg = f"{target} matched AS_PATH regex."
            status = self.codes["success"]
        if not validity:
            logger.error(f"{msg}, {status}")
        return (validity, msg, status)
