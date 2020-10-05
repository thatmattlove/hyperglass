"""Construct SSH command/API parameters from validated query data.

Accepts filtered & validated input from execute.py, constructs SSH
command for Netmiko library or API call parameters for supported
hyperglass API modules.
"""

# Standard Library
import re
import json as _json
from operator import attrgetter

# Project
from hyperglass.log import log
from hyperglass.constants import (  # APPEND_NEWLINE,
    TRANSPORT_REST,
    TARGET_FORMAT_SPACE,
    TARGET_JUNIPER_ASPATH,
)
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
            "Constructing {} query for '{}'",
            query_data.query_type,
            str(query_data.query_target),
        )
        self.device = device
        self.query_data = query_data
        self.target = self.query_data.query_target

        # Set transport method based on NOS type
        self.transport = "scrape"
        if self.device.nos in TRANSPORT_REST:
            self.transport = "rest"

        # Remove slashes from target for required platforms
        if self.device.nos in TARGET_FORMAT_SPACE:
            self.target = re.sub(r"\/", r" ", str(self.query_data.query_target))

        # Set AFIs for based on query type
        if self.query_data.query_type in ("bgp_route", "ping", "traceroute"):

            # For IP queries, AFIs are enabled (not null/None) VRF -> AFI definitions
            # where the IP version matches the IP version of the target.
            self.afis = [
                v
                for v in (
                    self.query_data.query_vrf.ipv4,
                    self.query_data.query_vrf.ipv6,
                )
                if v is not None and self.query_data.query_target.version == v.version
            ]
        elif self.query_data.query_type in ("bgp_aspath", "bgp_community"):

            # For AS Path/Community queries, AFIs are just enabled VRF -> AFI
            # definitions, no IP version checking is performed (since there is no IP).
            self.afis = [
                v
                for v in (
                    self.query_data.query_vrf.ipv4,
                    self.query_data.query_vrf.ipv6,
                )
                if v is not None
            ]

            # For devices that follow Juniper's AS_PATH regex standards,
            # filter out Cisco-style special characters.

            if (
                self.device.nos in TARGET_JUNIPER_ASPATH
                and self.query_data.query_type in ("bgp_aspath",)
            ):
                query = str(self.query_data.query_target)
                asns = re.findall(r"\d+", query)
                was_modified = False
                if bool(re.match(r"^\_", query)):
                    # Replace `_65000` with `.* 65000`
                    asns.insert(0, r".*")
                    was_modified = True
                if bool(re.match(r".*(\_)$", query)):
                    # Replace `65000_` with `65000 .*`
                    asns.append(r".*")
                    was_modified = True
                if was_modified:
                    self.target = " ".join(asns)
                else:
                    self.target = query

    def json(self, afi):
        """Return JSON version of validated query for REST devices.

        Arguments:
            afi {object} -- AFI object

        Returns:
            {str} -- JSON query string
        """
        log.debug("Building JSON query for {q}", q=repr(self.query_data))
        return _json.dumps(
            {
                "query_type": self.query_data.query_type,
                "vrf": self.query_data.query_vrf.name,
                "afi": afi.protocol,
                "source": str(afi.source_address),
                "target": str(self.target),
            }
        )

    def scrape(self, afi):
        """Return formatted command for 'Scrape' endpoints (SSH).

        Arguments:
            afi {object} -- AFI object

        Returns:
            {str} -- Command string
        """
        if self.device.structured_output:
            cmd_paths = (
                self.device.nos,
                "structured",
                afi.protocol,
                self.query_data.query_type,
            )
        else:
            cmd_paths = (self.device.commands, afi.protocol, self.query_data.query_type)

        command = attrgetter(".".join(cmd_paths))(commands)
        return command.format(
            target=self.target,
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

        log.debug("Constructed query: {}", query)
        return query
