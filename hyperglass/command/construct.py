# https://github.com/checktheroads/hyperglass
"""
Accepts filtered & validated input from execute.py, constructs SSH command for Netmiko library or \
API call parameters for hyperglass-frr
"""
# Standard Imports
import json
import inspect
import logging

# Module Imports
import logzero
from logzero import logger
from netaddr import IPNetwork, IPAddress  # pylint: disable=unused-import

# Dear PyLint, the netaddr library is a special snowflake. You might not see `IPAddress` get used, \
# but when you use something like `IPNetwork("192.0.2.1/24").ip`, the returned value is \
# IPAddress("192.0.2.1"), so I do actually need this import. <3, -ML

# Project Imports
from hyperglass import configuration

# Configuration Imports
codes = configuration.codes()

# Logzero Configuration
if configuration.debug_state():
    logzero.loglevel(logging.DEBUG)
else:
    logzero.loglevel(logging.INFO)


def current_function():
    """Returns name of current function"""
    this_function = inspect.stack()[1][3]
    return this_function


class Construct:
    """Constructor for FRRouting API"""

    def __init__(self, device):
        self.device = device
        self.d_address = self.device["address"]
        self.d_src_addr_ipv4 = self.device["src_addr_ipv4"]
        self.d_src_addr_ipv6 = self.device["src_addr_ipv6"]
        self.d_name = self.device["name"]
        self.d_type = self.device["type"]
        self.command = configuration.command(self.d_type)

    def get_src(self, ver):
        """Returns source IP based on IP version."""
        src = None
        if ver == 4:
            src = self.d_src_addr_ipv4
        if ver == 6:
            src = self.d_src_addr_ipv6
        logger.debug(f"Source IPv{ver}: {src}")
        return src

    def ping(self, transport, target):
        """Constructs ping query parameters from pre-validated input"""
        query_type = current_function()
        logger.debug(f"Constructing {query_type} query for {target} via {transport}...")
        query = None
        ip_version = IPNetwork(target).ip.version
        afi = f"ipv{ip_version}"
        source = self.get_src(ip_version)
        if transport == "rest":
            query = json.dumps(
                {
                    "query_type": query_type,
                    "afi": afi,
                    "source": source,
                    "target": target,
                }
            )
        if transport == "scrape":
            conf_command = self.command[afi][query_type]
            fmt_command = conf_command.format(target=target, source=source)
            query = (self.d_address, self.d_type, fmt_command)
        logger.debug(f"Constructed query: {query}")
        return query

    def traceroute(self, transport, target):
        """Constructs traceroute query parameters from pre-validated input"""
        query_type = current_function()
        logger.debug(f"Constructing {query_type} query for {target} via {transport}...")
        query = None
        ip_version = IPNetwork(target).ip.version
        afi = f"ipv{ip_version}"
        source = self.get_src(ip_version)
        if transport == "rest":
            query = json.dumps(
                {
                    "query_type": query_type,
                    "afi": afi,
                    "source": source,
                    "target": target,
                }
            )

        if transport == "scrape":
            conf_command = self.command[afi][query_type]
            fmt_command = conf_command.format(target=target, source=source)
            query = (self.d_address, self.d_type, fmt_command)
        logger.debug(f"Constructed query: {query}")
        return query

    def bgp_route(self, transport, target):
        """Constructs bgp_route query parameters from pre-validated input"""
        query_type = current_function()
        logger.debug(f"Constructing {query_type} query for {target} via {transport}...")
        query = None
        ip_version = IPNetwork(target).ip.version
        afi = f"ipv{ip_version}"
        if transport == "rest":
            query = json.dumps({"query_type": query_type, "afi": afi, "target": target})
        if transport == "scrape":
            conf_command = self.command[afi][query_type]
            fmt_command = conf_command.format(target=target)
            query = (self.d_address, self.d_type, fmt_command)
        logger.debug(f"Constructed query: {query}")
        return query

    def bgp_community(self, transport, target):
        """Constructs bgp_community query parameters from pre-validated input"""
        query_type = current_function()
        logger.debug(f"Constructing {query_type} query for {target} via {transport}...")
        afi = "dual"
        query = None
        if transport == "rest":
            query = json.dumps({"query_type": query_type, "afi": afi, "target": target})
        if transport == "scrape":
            conf_command = self.command[afi][query_type]
            fmt_command = conf_command.format(target=target)
            query = (self.d_address, self.d_type, fmt_command)
        logger.debug(f"Constructed query: {query}")
        return query

    def bgp_aspath(self, transport, target):
        """Constructs bgp_aspath query parameters from pre-validated input"""
        query_type = current_function()
        logger.debug(f"Constructing {query_type} query for {target} via {transport}...")
        afi = "dual"
        query = None
        if transport == "rest":
            query = json.dumps({"query_type": query_type, "afi": afi, "target": target})
        if transport == "scrape":
            conf_command = self.command[afi][query_type]
            fmt_command = conf_command.format(target=target)
            query = (self.d_address, self.d_type, fmt_command)
        logger.debug(f"Constructed query: {query}")
        return query
