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
from hyperglass.constants import TRANSPORT_REST, TARGET_FORMAT_SPACE
from hyperglass.configuration import commands


class Construct:
    """Construct SSH commands/REST API parameters from validated query data."""

    def __init__(self, device, query_data):
        """Initialize command construction."""
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

        with Formatter(self.device.nos, self.query_data.query_type) as formatter:
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
            self.target = formatter(self.query_data.query_target)

    def json(self, afi):
        """Return JSON version of validated query for REST devices."""
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
        """Return formatted command for 'Scrape' endpoints (SSH)."""
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
        """Return queries for each enabled AFI."""
        query = []

        for afi in self.afis:
            if self.transport == "rest":
                query.append(self.json(afi=afi))
            else:
                query.append(self.scrape(afi=afi))

        log.debug("Constructed query: {}", query)
        return query


class Formatter:
    """Modify query target based on the device's NOS requirements and the query type."""

    def __init__(self, nos: str, query_type: str) -> None:
        """Initialize target formatting."""
        self.nos = nos
        self.query_type = query_type

    def __enter__(self):
        """Get the relevant formatter."""
        return self._get_formatter()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Handle context exit."""
        if exc_type is not None:
            log.error(exc_traceback)
        pass

    def _get_formatter(self):
        if self.nos in ("juniper", "juniper_junos"):
            if self.query_type == "bgp_aspath":
                return self._juniper_bgp_aspath
        if self.nos in ("bird", "bird_ssh"):
            if self.query_type == "bgp_aspath":
                return self._bird_bgp_aspath
            elif self.query_type == "bgp_community":
                return self._bird_bgp_community
        return self._default

    def _default(self, target: str) -> str:
        """Don't format targets by default."""
        return target

    def _juniper_bgp_aspath(self, target: str) -> str:
        """Convert from Cisco AS_PATH format to Juniper format."""
        query = str(target)
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
            modified = " ".join(asns)
            log.debug("Modified target '{}' to '{}'", target, modified)
            return modified

        return query

    def _bird_bgp_aspath(self, target: str) -> str:
        """Convert from Cisco AS_PATH format to BIRD format."""

        # Extract ASNs from query target string
        asns = re.findall(r"\d+", target)
        was_modified = False

        if bool(re.match(r"^\_", target)):
            # Replace `_65000` with `.* 65000`
            asns.insert(0, "*")
            was_modified = True

        if bool(re.match(r".*(\_)$", target)):
            # Replace `65000_` with `65000 .*`
            asns.append("*")
            was_modified = True

        asns.insert(0, "[=")
        asns.append("=]")

        result = " ".join(asns)

        if was_modified:
            log.debug("Modified target '{}' to '{}'", target, result)

        return result

    def _bird_bgp_community(self, target: str) -> str:
        """Convert from standard community format to BIRD format."""
        parts = target.split(":")
        return f'({",".join(parts)})'
