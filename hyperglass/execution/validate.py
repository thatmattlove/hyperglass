"""Validate query data.

Accepts raw input data from execute.py, passes it through specific
filters based on query type, returns validity boolean and specific
error message.
"""
# Standard Library Imports
import ipaddress
import re

# Project Imports
from hyperglass.configuration import params
from hyperglass.exceptions import HyperglassError
from hyperglass.exceptions import InputInvalid
from hyperglass.exceptions import InputNotAllowed
from hyperglass.util import log


class IPType:
    """Build IPv4 & IPv6 attributes for input target.

    Passes input through IPv4/IPv6 regex patterns to determine if input
    is formatted as a host (e.g. 192.0.2.1), or as CIDR
    (e.g. 192.0.2.0/24). is_host() and is_cidr() return a boolean.
    """

    def __init__(self):
        """Initialize attribute builder."""
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
        """Test target to see if it is formatted as a host address.

        Arguments:
            target {str} -- Target IPv4/IPv6 address

        Returns:
            {bool} -- True if host, False if not
        """
        ip_version = ipaddress.ip_network(target).version
        state = False
        if ip_version == 4 and re.match(self.ipv4_host, target):
            log.debug(f"{target} is an IPv{ip_version} host.")
            state = True
        if ip_version == 6 and re.match(self.ipv6_host, target):
            log.debug(f"{target} is an IPv{ip_version} host.")
            state = True
        return state

    def is_cidr(self, target):
        """Test target to see if it is formatted as CIDR.

        Arguments:
            target {str} -- Target IPv4/IPv6 address

        Returns:
            {bool} -- True if CIDR, False if not
        """
        ip_version = ipaddress.ip_network(target).version
        state = False
        if ip_version == 4 and re.match(self.ipv4_cidr, target):
            state = True
        if ip_version == 6 and re.match(self.ipv6_cidr, target):
            state = True
        return state


def ip_validate(target):
    """Validate if input is a valid IP address.

    Arguments:
        target {str} -- Unvalidated IPv4/IPv6 address

    Raises:
        ValueError: Raised if target is not a valid IPv4 or IPv6 address

    Returns:
        {object} -- Valid IPv4Network/IPv6Network object
    """
    try:
        valid_ip = ipaddress.ip_network(target)
        if valid_ip.is_reserved or valid_ip.is_unspecified or valid_ip.is_loopback:
            _exception = ValueError(params.messages.invalid_input)
            _exception.details = {}
            raise _exception
    except (ipaddress.AddressValueError, ValueError) as ip_error:
        log.debug(f"IP {target} is invalid")
        _exception = ValueError(ip_error)
        _exception.details = {}
        raise _exception
    return valid_ip


def ip_access_list(query_data, device):
    """Check VRF access list for matching prefixes.

    Arguments:
        query_data {object} -- Query object
        device {object} -- Device object

    Raises:
        HyperglassError: Raised if query VRF and ACL VRF do not match
        ValueError: Raised if an ACL deny match is found
        ValueError: Raised if no ACL permit match is found

    Returns:
        {str} -- Allowed target
    """
    log.debug(f"Checking Access List for: {query_data.query_target}")

    def _member_of(target, network):
        """Check if IP address belongs to network.

        Arguments:
            target {object} -- Target IPv4/IPv6 address
            network {object} -- ACL network

        Returns:
            {bool} -- True if target is a member of network, False if not
        """
        log.debug(f"Checking membership of {target} for {network}")

        membership = False
        if (
            network.network_address <= target.network_address
            and network.broadcast_address >= target.broadcast_address  # NOQA: W503
        ):
            log.debug(f"{target} is a member of {network}")
            membership = True
        return membership

    target = ipaddress.ip_network(query_data.query_target)

    vrf_acl = None
    for vrf in device.vrfs:
        if vrf.name == query_data.query_vrf:
            vrf_acl = vrf.access_list
    if not vrf_acl:
        raise HyperglassError(
            message="Unable to match query VRF to any configured VRFs",
            alert="danger",
            keywords=[query_data.query_vrf],
        )

    target_ver = target.version

    log.debug(f"Access List: {vrf_acl}")

    for ace in vrf_acl:
        for action, net in {
            a: n for a, n in ace.items() for ace in vrf_acl if n.version == target_ver
        }.items():
            # If the target is a member of an allowed network, exit successfully.
            if _member_of(target, net) and action == "allow":
                log.debug(f"{target} is specifically allowed")
                return target

            # If the target is a member of a denied network, return an error.
            elif _member_of(target, net) and action == "deny":
                log.debug(f"{target} is specifically denied")
                _exception = ValueError(params.messages.acl_denied)
                _exception.details = {"denied_network": str(net)}
                raise _exception

    # Implicitly deny queries if an allow statement does not exist.
    log.debug(f"{target} is implicitly denied")
    _exception = ValueError(params.messages.acl_not_allowed)
    _exception.details = {"denied_network": ""}
    raise _exception


def ip_attributes(target):
    """Construct dictionary of validated IP attributes for repeated use.

    Arguments:
        target {str} -- Target IPv4/IPv6 address

    Returns:
        {dict} -- IP attribute dict
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
    """Check multiple IP address related validation parameters.

    Arguments:
        query_type {str} -- Query type
        target {str} -- Query target
        device {object} -- Device

    Raises:
        ValueError: Raised if max prefix length check fails
        ValueError: Raised if Requires IPv6 CIDR check fails
        ValueError: Raised if directed CIDR check fails

    Returns:
        {str} -- target if checks pass
    """
    prefix_attr = ip_attributes(target)
    log.debug(f"IP Attributes:\n{prefix_attr}")

    # If enable_max_prefix feature enabled, require that BGP Route
    # queries be smaller than configured size limit.
    if query_type == "bgp_route" and params.features.max_prefix.enable:
        max_length = getattr(params.features.max_prefix, prefix_attr["afi"])
        if prefix_attr["length"] > max_length:
            log.debug("Failed max prefix length check")
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
        log.debug("Failed requires IPv6 CIDR check")
        _exception = ValueError(params.messages.requires_ipv6_cidr)
        _exception.details = {"device_name": device.display_name}
        raise _exception

    # If query type is ping or traceroute, and query target is in CIDR
    # format, return an error.
    if query_type in ("ping", "traceroute") and IPType().is_cidr(target):
        log.debug("Failed CIDR format for ping/traceroute check")
        _exception = ValueError(params.messages.directed_cidr)
        _exception.details = {"query_type": getattr(params.branding.text, query_type)}
        raise _exception
    return target


class Validate:
    """Validates query data with selected device.

    Accepts raw input and associated device parameters from execute.py
    and validates the input based on specific query type. Returns
    boolean for validity, specific error message, and status code.
    """

    def __init__(self, device, query_data, target):
        """Initialize device parameters and error codes."""
        self.device = device
        self.query_data = query_data
        self.query_type = self.query_data.query_type
        self.target = target

    def validate_ip(self):
        """Validate IPv4/IPv6 Input.

        Raises:
            InputInvalid: Raised if IP validation fails
            InputNotAllowed: Raised if ACL checks fail
            InputNotAllowed: Raised if IP type checks fail

        Returns:
            {str} -- target if validation passes
        """
        log.debug(f"Validating {self.query_type} query for target {self.target}...")

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

        # If target is a not allowed, return an error.
        try:
            ip_access_list(self.query_data, self.device)
        except ValueError as unformatted_error:
            raise InputNotAllowed(
                str(unformatted_error), target=self.target, **unformatted_error.details
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
        """Validate dual-stack input such as bgp_community & bgp_aspath.

        Raises:
            InputInvalid: Raised if target community is invalid.
            InputInvalid: Raised if target AS_PATh is invalid.

        Returns:
            {str} -- target if validation passes.
        """
        log.debug(f"Validating {self.query_type} query for target {self.target}...")

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
        """Validate input.

        Returns:
            {str} -- target if validation passes
        """
        if self.query_type in ("bgp_community", "bgp_aspath"):
            return self.validate_dual()
        else:
            return self.validate_ip()
