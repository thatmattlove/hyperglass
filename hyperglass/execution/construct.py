"""Construct SSH command/API parameters from validated query data.

Accepts filtered & validated input from execute.py, constructs SSH
command for Netmiko library or API call parameters for supported
hyperglass API modules.
"""

# Standard Library
import re
import operator

# Third Party
import ujson

# Project
from hyperglass.util import log
from hyperglass.constants import TRANSPORT_REST, TARGET_FORMAT_SPACE
from hyperglass.configuration import commands


class Construct:
    """Construct SSH commands/REST API parameters from validated query data."""

    def __init__(self, device, query_data):
        """Initialize command construction.

        Arguments:
            device {object} -- Device object
            query_data {object} -- Validated query object
        """
        log.debug(
            "Constructing {q} query for '{t}'",
            q=query_data.query_type,
            t=str(query_data.query_target),
        )
        self.device = device
        self.query_data = query_data

        # Set transport method based on NOS type
        self.transport = "scrape"
        if self.device.nos in TRANSPORT_REST:
            self.transport = "rest"

        # Remove slashes from target for required platforms
        if self.device.nos in TARGET_FORMAT_SPACE:
            self.query_data.query_target = re.sub(
                r"\/", r" ", str(self.query_data.query_target)
            )

        # Set AFIs for based on query type
        if self.query_data.query_type in ("bgp_route", "ping", "traceroute"):
            """
            For IP queries, AFIs are enabled (not null/None) VRF -> AFI definitions
            where the IP version matches the IP version of the target.
            """
            self.afis = [
                v
                for v in (
                    self.query_data.query_vrf.ipv4,
                    self.query_data.query_vrf.ipv6,
                )
                if v is not None and self.query_data.query_target.version == v.version
            ]
        elif self.query_data.query_type in ("bgp_aspath", "bgp_community"):
            """
            For AS Path/Community queries, AFIs are just enabled VRF -> AFI definitions,
            no IP version checking is performed (since there is no IP).
            """
            self.afis = [
                v
                for v in (
                    self.query_data.query_vrf.ipv4,
                    self.query_data.query_vrf.ipv6,
                )
                if v is not None
            ]

    def json(self, afi):
        """Return JSON version of validated query for REST devices.

        Arguments:
            afi {object} -- AFI object

        Returns:
            {str} -- JSON query string
        """
        log.debug("Building JSON query for {q}", q=repr(self.query_data))
        return ujson.dumps(
            {
                "query_type": self.query_data.query_type,
                "vrf": self.query_data.query_vrf.name,
                "afi": afi.protocol,
                "source": str(afi.source_address),
                "target": str(self.query_data.query_target),
            }
        )

    def scrape(self, afi):
        """Return formatted command for 'Scrape' endpoints (SSH).

        Arguments:
            afi {object} -- AFI object

        Returns:
            {str} -- Command string
        """
        command = operator.attrgetter(
            f"{self.device.nos}.{afi.protocol}.{self.query_data.query_type}"
        )(commands)
        return command.format(
            target=self.query_data.query_target,
            source=str(afi.source_address),
            vrf=self.query_data.query_vrf.name,
        )

    def queries(self):
        """Return queries for each enabled AFI.

        Returns:
            {list} -- List of queries to run
        """
        query = []

        for afi in self.afis:
            if self.transport == "rest":
                query.append(self.json(afi=afi))
            else:
                query.append(self.scrape(afi=afi))

        log.debug(f"Constructed query: {query}")
        return query
