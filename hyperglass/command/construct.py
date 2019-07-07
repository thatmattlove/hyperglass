# https://github.com/checktheroads/hyperglass
"""
Accepts filtered & validated input from execute.py, constructs SSH command for Netmiko library or \
API call parameters for hyperglass-frr
"""
# Standard Imports
import json
import operator

# Module Imports
import logzero
from logzero import logger
from netaddr import IPNetwork, IPAddress  # pylint: disable=unused-import

# Dear PyLint, the netaddr library is a special snowflake. You might not see `IPAddress` get used, \
# but when you use something like `IPNetwork("192.0.2.1/24").ip`, the returned value is \
# IPAddress("192.0.2.1"), so I do actually need this import. <3, -ML

# Project Imports
from hyperglass.configuration import params, commands, logzero_config


class Construct:
    """
    Constructs SSH commands or REST API queries based on validated
    input parameters.
    """

    def __init__(self, device):
        self.device = device

    def get_src(self, ver):
        """
        Returns source IP based on IP version of query destination.
        """
        src = None
        if ver == 4:
            src = self.device.src_addr_ipv4.exploded
        if ver == 6:
            src = self.device.src_addr_ipv6.exploded
        logger.debug(f"IPv{ver} Source: {src}")
        return src

    def device_commands(self, nos, afi, query_type):
        cmd_path = f"{nos}.{afi}.{query_type}"
        return operator.attrgetter(cmd_path)(commands)

    def ping(self, transport, target):
        """Constructs ping query parameters from pre-validated input"""
        query_type = "ping"
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
        elif transport == "scrape":
            conf_command = self.device_commands(self.device.nos, afi, query_type)
            fmt_command = conf_command.format(target=target, source=source)
            query = (self.device.address.exploded, self.device.nos, fmt_command)
        logger.debug(f"Constructed query: {query}")
        return query

    def traceroute(self, transport, target):
        """
        Constructs traceroute query parameters from pre-validated input.
        """
        query_type = "traceroute"
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

        elif transport == "scrape":
            conf_command = self.device_commands(self.device.nos, afi, query_type)
            fmt_command = conf_command.format(target=target, source=source)
            query = (self.device.address.exploded, self.device.nos, fmt_command)
        logger.debug(f"Constructed query: {query}")
        return query

    def bgp_route(self, transport, target):
        """
        Constructs bgp_route query parameters from pre-validated input.
        """
        query_type = "bgp_route"
        logger.debug(f"Constructing {query_type} query for {target} via {transport}...")
        query = None
        ip_version = IPNetwork(target).ip.version
        afi = f"ipv{ip_version}"
        if transport == "rest":
            query = json.dumps({"query_type": query_type, "afi": afi, "target": target})
        if transport == "scrape":
            conf_command = self.device_commands(self.device.nos, afi, query_type)
            fmt_command = conf_command.format(target=target)
            query = (self.device.address.exploded, self.device.nos, fmt_command)
        logger.debug(f"Constructed query: {query}")
        return query

    def bgp_community(self, transport, target):
        """
        Constructs bgp_community query parameters from pre-validated
        input.
        """
        query_type = "bgp_community"
        logger.debug(f"Constructing {query_type} query for {target} via {transport}...")
        afi = "dual"
        query = None
        if transport == "rest":
            query = json.dumps({"query_type": query_type, "afi": afi, "target": target})
        if transport == "scrape":
            conf_command = self.device_commands(self.device.nos, afi, query_type)
            fmt_command = conf_command.format(target=target)
            query = (self.device.address.exploded, self.device.nos, fmt_command)
        logger.debug(f"Constructed query: {query}")
        return query

    def bgp_aspath(self, transport, target):
        """
        Constructs bgp_aspath query parameters from pre-validated input.
        """
        query_type = "bgp_aspath"
        logger.debug(f"Constructing {query_type} query for {target} via {transport}...")
        afi = "dual"
        query = None
        if transport == "rest":
            query = json.dumps({"query_type": query_type, "afi": afi, "target": target})
        if transport == "scrape":
            conf_command = self.device_commands(self.device.nos, afi, query_type)
            fmt_command = conf_command.format(target=target)
            query = (self.device.address.exploded, self.device.nos, fmt_command)
        logger.debug(f"Constructed query: {query}")
        return query
