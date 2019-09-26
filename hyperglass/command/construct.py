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
from logzero import logger as log

# Project Imports
from hyperglass.configuration import vrfs
from hyperglass.configuration import commands
from hyperglass.configuration import logzero_config  # noqa: F401


class Construct:
    """
    Constructs SSH commands or REST API queries based on validated
    input parameters.
    """

    def __init__(self, device, query_data, transport):
        self.device = device
        self.query_data = query_data
        self.transport = transport
        self.query_target = self.query_data["query_target"]
        self.query_vrf = self.query_data["query_vrf"]

    @staticmethod
    def get_src(device, afi):
        """
        Returns source IP based on IP version of query destination.
        """
        src_afi = f"src_addr_{afi}"
        src = getattr(device, src_afi)
        return src.exploded

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

    @staticmethod
    def query_afi(query_target, query_vrf):
        """
        Constructs AFI string. If query_vrf is specified, AFI prefix is
        "vpnv", if not, AFI prefix is "ipv"
        """
        protocol = ipaddress.ip_network(query_target).version
        if query_vrf:
            afi = f"ipv{protocol}_vpn"
        else:
            afi = f"ipv{protocol}"
        return afi

    def ping(self):
        """Constructs ping query parameters from pre-validated input"""

        log.debug(
            f"Constructing ping query for {self.query_target} via {self.transport}"
        )

        query = []
        query_vrfs = self.query_vrf

        for vrf in query_vrfs:
            query_afi = self.query_afi(self.query_target, vrf)
            afi_path = f"self.device.afis.{query_afi}"
            afi = getattr(afi_path, "label")
            vrf_label = vrfs.get(vrf).get("label")
            vrf_source = getattr(afi_path, "source")

            if self.transport == "rest":
                vrf_query = json.dumps(
                    {
                        "query_type": "ping",
                        "afi": afi,
                        "vrf": vrf_label,
                        "source": vrf_source,
                        "target": self.query_target,
                    }
                )
            elif self.transport == "scrape":
                cmd = self.device_commands(self.device.commands, afi, "ping")
                query.append(
                    cmd.format(
                        target=self.query_target, source=vrf_source, vrf=vrf_label
                    )
                )
            query.append(vrf_query)

        log.debug(f"Constructed query: {query}")
        return query

    def traceroute(self):
        """
        Constructs traceroute query parameters from pre-validated input.
        """
        log.debug(
            (
                f"Constructing traceroute query for {self.query_target} "
                f"via {self.transport}"
            )
        )

        query = None
        afi = self.query_afi(self.query_target, self.query_vrf)
        source = self.get_src(self.device, afi)

        if self.transport == "rest":
            query = json.dumps(
                {
                    "query_type": "traceroute",
                    "afi": afi,
                    "vrf": self.query_vrf,
                    "source": source,
                    "target": self.query_target,
                }
            )
        elif self.transport == "scrape":
            cmd = self.device_commands(self.device.commands, afi, "traceroute")
            query = cmd.format(
                target=self.query_target, source=source, vrf=self.query_vrf
            )

        log.debug(f"Constructed query: {query}")

        return [query]

    def bgp_route(self):
        """
        Constructs bgp_route query parameters from pre-validated input.
        """
        log.debug(
            f"Constructing bgp_route query for {self.query_target} via {self.transport}"
        )

        query = None
        afi = Construct.query_afi(self.query_target, self.query_vrf)
        source = self.get_src(self.device, afi)

        if self.transport == "rest":
            query = json.dumps(
                {
                    "query_type": "bgp_route",
                    "afi": afi,
                    "vrf": self.query_vrf,
                    "source": source,
                    "target": self.query_target,
                }
            )
        elif self.transport == "scrape":
            cmd = self.device_commands(self.device.commands, afi, "bgp_route")
            query = cmd.format(
                target=self.query_target, source=source, afi=afi, vrf=self.query_vrf
            )

        log.debug(f"Constructed query: {query}")

        return [query]

    def bgp_community(self):
        """
        Constructs bgp_community query parameters from pre-validated
        input.
        """
        log.debug(
            (
                f"Constructing bgp_community query for {self.query_target} "
                f"via {self.transport}"
            )
        )

        query = None
        afi = self.query_afi(self.query_target, self.query_vrf)
        log.debug(afi)
        source = self.get_src(self.device, afi)

        if self.transport == "rest":
            query = json.dumps(
                {
                    "query_type": "bgp_community",
                    "afi": afi,
                    "vrf": self.query_vrf,
                    "source": source,
                    "target": self.query_target,
                }
            )
        elif self.transport == "scrape":
            cmd = self.device_commands(self.device.commands, afi, "bgp_community")
            query = cmd.format(
                target=self.query_target, source=source, vrf=self.query_vrf
            )

        log.debug(f"Constructed query: {query}")

        return query

    def bgp_aspath(self):
        """
        Constructs bgp_aspath query parameters from pre-validated input.
        """
        log.debug(
            (
                f"Constructing bgp_aspath query for {self.query_target} "
                f"via {self.transport}"
            )
        )

        query = None
        afi = self.query_afi(self.query_target, self.query_vrf)
        source = self.get_src(self.device, afi)

        if self.transport == "rest":
            query = json.dumps(
                {
                    "query_type": "bgp_aspath",
                    "afi": afi,
                    "vrf": self.query_vrf,
                    "source": source,
                    "target": self.query_target,
                }
            )
        elif self.transport == "scrape":
            cmd = self.device_commands(self.device.commands, afi, "bgp_aspath")
            query = cmd.format(
                target=self.query_target, source=source, vrf=self.query_vrf
            )

        log.debug(f"Constructed query: {query}")

        return query
