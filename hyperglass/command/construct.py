"""
Accepts filtered & validated input from execute.py, constructs SSH
command for Netmiko library or API call parameters for supported
hyperglass API modules.
"""
# Standard Library Imports
import re
import ipaddress
import json
import operator

# Third Party Imports
from logzero import logger as log

# Project Imports
from hyperglass.configuration import vrfs
from hyperglass.configuration import commands
from hyperglass.configuration import logzero_config  # noqa: F401
from hyperglass.constants import target_format_space


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

    def format_target(self, target):
        """Formats query target based on NOS requirement"""
        if self.device.nos in target_format_space:
            _target = re.sub(r"\/", r" ", target)
        else:
            _target = target
        log.debug(f"Formatted target: {_target}")
        return _target

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
    def get_cmd_type(query_protocol, query_vrf):
        """
        Constructs AFI string. If query_vrf is specified, AFI prefix is
        "vpnv", if not, AFI prefix is "ipv"
        """
        if query_vrf and query_vrf != "default":
            cmd_type = f"{query_protocol}_vrf"
        else:
            cmd_type = f"{query_protocol}_default"
        return cmd_type

    def ping(self):
        """Constructs ping query parameters from pre-validated input"""

        log.debug(
            f"Constructing ping query for {self.query_target} via {self.transport}"
        )

        query = []
        query_protocol = f"ipv{ipaddress.ip_network(self.query_target).version}"
        vrf = getattr(self.device.vrfs, self.query_vrf)
        afi = getattr(vrf, query_protocol)

        if self.transport == "rest":
            query.append(
                json.dumps(
                    {
                        "query_type": "ping",
                        "afi": afi.afi_name,
                        "vrf": afi.vrf_name,
                        "source": afi.source_address,
                        "target": self.query_target,
                    }
                )
            )
        elif self.transport == "scrape":
            cmd_type = self.get_cmd_type(afi.afi_name, self.query_vrf)
            cmd = self.device_commands(self.device.commands, cmd_type, "ping")
            query.append(
                cmd.format(
                    target=self.query_target,
                    source=afi.source_address,
                    vrf=afi.vrf_name,
                    afi=afi.afi_name,
                )
            )

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

        query = []
        query_protocol = f"ipv{ipaddress.ip_network(self.query_target).version}"
        vrf = getattr(self.device.vrfs, self.query_vrf)
        afi = getattr(vrf, query_protocol)

        if self.transport == "rest":
            query.append(
                json.dumps(
                    {
                        "query_type": "traceroute",
                        "afi": afi.afi_name,
                        "vrf": afi.vrf_name,
                        "source": afi.source_address,
                        "target": self.query_target,
                    }
                )
            )
        elif self.transport == "scrape":
            cmd_type = self.get_cmd_type(afi.afi_name, self.query_vrf)
            cmd = self.device_commands(self.device.commands, cmd_type, "traceroute")
            query.append(
                cmd.format(
                    target=self.query_target,
                    source=afi.source_address,
                    vrf=afi.vrf_name,
                    afi=afi.afi_name,
                )
            )

        log.debug(f"Constructed query: {query}")
        return query

    def bgp_route(self):
        """
        Constructs bgp_route query parameters from pre-validated input.
        """
        log.debug(
            f"Constructing bgp_route query for {self.query_target} via {self.transport}"
        )

        query = []
        query_protocol = f"ipv{ipaddress.ip_network(self.query_target).version}"
        vrf = getattr(self.device.vrfs, self.query_vrf)
        afi = getattr(vrf, query_protocol)

        if self.transport == "rest":
            query.append(
                json.dumps(
                    {
                        "query_type": "bgp_route",
                        "afi": afi.afi_name,
                        "vrf": afi.vrf_name,
                        "source": afi.source_address,
                        "target": self.query_target,
                    }
                )
            )
        elif self.transport == "scrape":
            cmd_type = self.get_cmd_type(afi.afi_name, self.query_vrf)
            cmd = self.device_commands(self.device.commands, cmd_type, "bgp_route")
            query.append(
                cmd.format(
                    target=self.format_target(self.query_target),
                    source=afi.source_address,
                    vrf=afi.vrf_name,
                    afi=afi.afi_name,
                )
            )

        log.debug(f"Constructed query: {query}")
        return query

    def bgp_community(self):
        """
        Constructs bgp_community query parameters from pre-validated
        input.
        """
        log.debug(
            (
                f"Constructing bgp_community query for "
                f"{self.query_target} via {self.transport}"
            )
        )

        query = []

        vrf = getattr(self.device.vrfs, self.query_vrf)
        afis = []

        vrf_dict = getattr(vrfs, self.query_vrf).dict()
        for vrf_key, vrf_value in {
            p: e for p, e in vrf_dict.items() if p in ("ipv4", "ipv6")
        }.items():
            if vrf_value:
                afis.append(vrf_key)

        for afi in afis:
            afi_attr = getattr(vrf, afi)
            if self.transport == "rest":
                query.append(
                    json.dumps(
                        {
                            "query_type": "bgp_community",
                            "afi": afi_attr.afi_name,
                            "vrf": afi_attr.vrf_name,
                            "source": afi_attr.source_address,
                            "target": self.query_target,
                        }
                    )
                )
            elif self.transport == "scrape":
                cmd_type = self.get_cmd_type(afi.afi_name, self.query_vrf)
                cmd = self.device_commands(
                    self.device.commands, cmd_type, "bgp_community"
                )
                query.append(
                    cmd.format(
                        target=self.query_target,
                        source=afi_attr.source_address,
                        vrf=afi_attr.vrf_name,
                        afi=afi_attr.afi_name,
                    )
                )

        log.debug(f"Constructed query: {query}")
        return query

    def bgp_aspath(self):
        """
        Constructs bgp_aspath query parameters from pre-validated input.
        """
        log.debug(
            (
                f"Constructing bgp_aspath query for "
                f"{self.query_target} via {self.transport}"
            )
        )

        query = []

        vrf = getattr(self.device.vrfs, self.query_vrf)
        afis = []

        vrf_dict = getattr(vrfs, self.query_vrf).dict()
        for vrf_key, vrf_value in {
            p: e for p, e in vrf_dict.items() if p in ("ipv4", "ipv6")
        }.items():
            if vrf_value:
                afis.append(vrf_key)

        for afi in afis:
            afi_attr = getattr(vrf, afi)
            if self.transport == "rest":
                query.append(
                    json.dumps(
                        {
                            "query_type": "bgp_aspath",
                            "afi": afi_attr.afi_name,
                            "vrf": afi_attr.vrf_name,
                            "source": afi_attr.source_address,
                            "target": self.query_target,
                        }
                    )
                )
            elif self.transport == "scrape":
                cmd_type = self.get_cmd_type(afi.afi_name, self.query_vrf)
                cmd = self.device_commands(self.device.commands, cmd_type, "bgp_aspath")
                query.append(
                    cmd.format(
                        target=self.query_target,
                        source=afi_attr.source_address,
                        vrf=afi_attr.vrf_name,
                        afi=afi_attr.afi_name,
                    )
                )

        log.debug(f"Constructed query: {query}")
        return query
