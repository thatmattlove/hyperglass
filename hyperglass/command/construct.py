"""
Accepts filtered & validated input from execute.py, constructs SSH
command for Netmiko library or API call parameters for supported
hyperglass API modules.
"""
# Standard Library Imports
import ipaddress
import json
import operator

# Third Party Imports
from logzero import logger

# Project Imports
from hyperglass.configuration import commands
from hyperglass.configuration import logzero_config  # noqa: F401


class Construct:
    """
    Constructs SSH commands or REST API queries based on validated
    input parameters.
    """

    def __init__(self, device, transport):
        self.device = device
        self.transport = transport

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

    @staticmethod
    def device_commands(nos, afi, query_type):
        """
        Constructs class attribute path from input parameters, returns
        class attribute value for command. This is required because
        class attributes are set dynamically when devices.yaml is
        imported, so the attribute path is unknown until runtime.
        """
        cmd_path = f"{nos}.{afi}.{query_type}"
        return operator.attrgetter(cmd_path)(commands)

    def ping(self, target):
        """Constructs ping query parameters from pre-validated input"""
        query_type = "ping"
        logger.debug(
            f"Constructing {query_type} query for {target} via {self.transport}..."
        )
        query = None
        ip_version = ipaddress.ip_network(target).version
        afi = f"ipv{ip_version}"
        source = self.get_src(ip_version)
        if self.transport == "rest":
            query = json.dumps(
                {
                    "query_type": query_type,
                    "afi": afi,
                    "source": source,
                    "target": target,
                }
            )
        elif self.transport == "scrape":
            conf_command = self.device_commands(self.device.nos, afi, query_type)
            query = conf_command.format(target=target, source=source)
        logger.debug(f"Constructed query: {query}")
        return query

    def traceroute(self, target):
        """
        Constructs traceroute query parameters from pre-validated input.
        """
        query_type = "traceroute"
        logger.debug(
            f"Constructing {query_type} query for {target} via {self.transport}..."
        )
        query = None
        ip_version = ipaddress.ip_network(target).version
        afi = f"ipv{ip_version}"
        source = self.get_src(ip_version)
        if self.transport == "rest":
            query = json.dumps(
                {
                    "query_type": query_type,
                    "afi": afi,
                    "source": source,
                    "target": target,
                }
            )

        elif self.transport == "scrape":
            conf_command = self.device_commands(self.device.nos, afi, query_type)
            query = conf_command.format(target=target, source=source)
        logger.debug(f"Constructed query: {query}")
        return query

    def bgp_route(self, target):
        """
        Constructs bgp_route query parameters from pre-validated input.
        """
        query_type = "bgp_route"
        logger.debug(
            f"Constructing {query_type} query for {target} via {self.transport}..."
        )
        query = None
        ip_version = ipaddress.ip_network(target).version
        afi = f"ipv{ip_version}"
        if self.transport == "rest":
            query = json.dumps({"query_type": query_type, "afi": afi, "target": target})
        elif self.transport == "scrape":
            conf_command = self.device_commands(self.device.nos, afi, query_type)
            query = conf_command.format(target=target)
        logger.debug(f"Constructed query: {query}")
        return query

    def bgp_community(self, target):
        """
        Constructs bgp_community query parameters from pre-validated
        input.
        """
        query_type = "bgp_community"
        logger.debug(
            f"Constructing {query_type} query for {target} via {self.transport}..."
        )
        afi = "dual"
        query = None
        if self.transport == "rest":
            query = json.dumps({"query_type": query_type, "afi": afi, "target": target})
        elif self.transport == "scrape":
            conf_command = self.device_commands(self.device.nos, afi, query_type)
            query = conf_command.format(target=target)
        logger.debug(f"Constructed query: {query}")
        return query

    def bgp_aspath(self, target):
        """
        Constructs bgp_aspath query parameters from pre-validated input.
        """
        query_type = "bgp_aspath"
        logger.debug(
            f"Constructing {query_type} query for {target} via {self.transport}..."
        )
        afi = "dual"
        query = None
        if self.transport == "rest":
            query = json.dumps({"query_type": query_type, "afi": afi, "target": target})
        elif self.transport == "scrape":
            conf_command = self.device_commands(self.device.nos, afi, query_type)
            query = conf_command.format(target=target)
        logger.debug(f"Constructed query: {query}")
        return query
