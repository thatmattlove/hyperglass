"""Construct SSH command/API parameters from validated query data.

Accepts filtered & validated input from execute.py, constructs SSH
command for Netmiko library or API call parameters for supported
hyperglass API modules.
"""

# Standard Library
import re
import json as _json
import typing as t

# Project
from hyperglass.log import log
from hyperglass.util import get_fmt_keys
from hyperglass.constants import TRANSPORT_REST, TARGET_FORMAT_SPACE
from hyperglass.exceptions.public import InputInvalid
from hyperglass.exceptions.private import ConfigError

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.api.query import Query
    from hyperglass.models.directive import Directive
    from hyperglass.models.config.devices import Device


class Construct:
    """Construct SSH commands/REST API parameters from validated query data."""

    directive: "Directive"
    device: "Device"
    query: "Query"
    transport: str
    target: str

    def __init__(self, device: "Device", query: "Query"):
        """Initialize command construction."""
        log.debug(
            "Constructing '{}' query for '{}'",
            query.query_type,
            str(query.query_target),
        )
        self.query = query
        self.device = device
        self.target = self.query.query_target
        self.directive = query.directive

        # Set transport method based on NOS type
        self.transport = "scrape"
        if self.device.platform in TRANSPORT_REST:
            self.transport = "rest"

        # Remove slashes from target for required platforms
        if self.device.platform in TARGET_FORMAT_SPACE:
            self.target = re.sub(r"\/", r" ", str(self.query.query_target))

        with Formatter(self.device.platform, self.query.query_type) as formatter:
            self.target = formatter(self.query.query_target)

    def json(self, afi):
        """Return JSON version of validated query for REST devices."""
        log.debug("Building JSON query for {q}", q=repr(self.query))
        return _json.dumps(
            {
                "query_type": self.query.query_type,
                "vrf": self.query.query_vrf.name,
                "afi": afi.protocol,
                "source": str(afi.source_address),
                "target": str(self.target),
            }
        )

    def format(self, command: str) -> str:
        """Return formatted command for 'Scrape' endpoints (SSH)."""
        keys = get_fmt_keys(command)
        attrs = {k: v for k, v in self.device.attrs.items() if k in keys}
        for key in [k for k in keys if k != "target"]:
            if key not in attrs:
                raise ConfigError(
                    ("Command '{c}' has attribute '{k}', " "which is missing from device '{d}'"),
                    level="danger",
                    c=self.directive.name,
                    k=key,
                    d=self.device.name,
                )
        return command.format(target=self.target, **attrs)

    def queries(self):
        """Return queries for each enabled AFI."""
        query = []

        rules = [r for r in self.directive.rules if r._passed is True]
        if len(rules) < 1:
            raise InputInvalid(
                error="No validation rules matched target '{target}'",
                target=self.query.query_target,
            )

        for rule in [r for r in self.directive.rules if r._passed is True]:
            for command in rule.commands:
                query.append(self.format(command))

        log.debug("Constructed query: {}", query)
        return query


class Formatter:
    """Modify query target based on the device's NOS requirements and the query type."""

    def __init__(self, platform: str, query_type: str) -> None:
        """Initialize target formatting."""
        self.platform = platform
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
        if self.platform in ("juniper", "juniper_junos"):
            if self.query_type == "bgp_aspath":
                return self._juniper_bgp_aspath
        if self.platform in ("bird", "bird_ssh"):
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
