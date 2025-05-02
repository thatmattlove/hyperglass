"""Construct SSH command/API parameters from validated query data.

Accepts filtered & validated input from execute.py, constructs SSH
command for Netmiko library or API call parameters for supported
hyperglass API modules.
"""

# Standard Library
import re
import json as _json
import typing as t
import ipaddress

# Project
from hyperglass.log import log
from hyperglass.util import get_fmt_keys
from hyperglass.constants import TRANSPORT_REST, TARGET_FORMAT_SPACE
from hyperglass.exceptions.public import InputInvalid
from hyperglass.exceptions.private import ConfigError

if t.TYPE_CHECKING:
    # Third Party
    from loguru import Logger

    # Project
    from hyperglass.models.api.query import Query
    from hyperglass.models.directive import Directive
    from hyperglass.models.config.devices import Device

FormatterCallback = t.Callable[[str], t.Union[t.List[str], str]]


class Construct:
    """Construct SSH commands/REST API parameters from validated query data."""

    directive: "Directive"
    device: "Device"
    query: "Query"
    transport: str
    target: str
    _log: "Logger"

    def __init__(self, device: "Device", query: "Query"):
        """Initialize command construction."""
        self._log = log.bind(type=query.query_type, target=query.query_target)
        self._log.debug("Constructing query")
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

        with Formatter(self.query) as formatter:
            self.target = formatter(self.prepare_target())

    def prepare_target(self) -> t.Union[t.List[str], str]:
        """Format the query target based on directive parameters."""
        if isinstance(self.query.query_target, t.List):
            # Directive can accept multiple values in a single command.
            if self.directive.multiple:
                return self.directive.multiple_separator.join(self.query.query_target)
            # Target is an array of one, return single item.
            if len(self.query.query_target) == 1:
                return self.query.query_target[0]
            # Directive commands should be run once for each item in the target.

        return self.query.query_target

    def json(self, afi):
        """Return JSON version of validated query for REST devices."""
        self._log.debug("Building JSON query")
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
        for key in [k for k in keys if k != "target" and k != "mask"]:
            if key not in attrs:
                raise ConfigError(
                    ("Command '{c}' has attribute '{k}', " "which is missing from device '{d}'"),
                    level="danger",
                    c=self.directive.name,
                    k=key,
                    d=self.device.name,
                )

        mask = ipaddress.ip_address("255.255.255.255")
        try:
            network = ipaddress.ip_network(self.target)
            if network.version == 4 and network.network_address != network.broadcast_address:
                # Network is an IPv4 network with more than one host.
                mask = network.netmask
        except ValueError:
            pass

        return command.format(target=self.target, mask=mask, **attrs)

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
        self._log.bind(constructed_query=query).debug("Constructed query")
        return query


class Formatter:
    """Modify query target based on the device's NOS requirements and the query type."""

    def __init__(self, query: "Query") -> None:
        """Initialize target formatting."""
        self.query = query
        self.platform = query.device.platform
        self.query_type = query.query_type

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
                return self._with_formatter(self._juniper_bgp_aspath)
        if self.platform in ("bird", "bird_ssh"):
            if self.query_type == "bgp_aspath":
                return self._with_formatter(self._bird_bgp_aspath)
            if self.query_type == "bgp_community":
                return self._with_formatter(self._bird_bgp_community)
        return self._with_formatter(self._default)

    def _default(self, target: str) -> str:
        """Don't format targets by default."""
        return target

    def _with_formatter(self, formatter: t.Callable[[str], str]) -> FormatterCallback:
        result: FormatterCallback
        if isinstance(self.query.query_target, t.List):
            result = lambda s: [formatter(i) for i in s]
        result = lambda s: formatter(s)
        return result

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
            log.bind(original=target, modified=modified).debug("Modified target")
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
            log.bind(original=target, modified=result).debug("Modified target")

        return result

    def _bird_bgp_community(self, target: str) -> str:
        """Convert from standard community format to BIRD format."""
        parts = target.split(":")
        return f'({",".join(parts)})'
