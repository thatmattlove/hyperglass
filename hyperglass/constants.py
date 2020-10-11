"""Constant definitions used throughout the application."""

# Standard Library
from datetime import datetime

__name__ = "hyperglass"
__version__ = "1.0.0-beta.61"
__author__ = "Matt Love"
__copyright__ = f"Copyright {datetime.now().year} Matthew Love"
__license__ = "BSD 3-Clause Clear License"

METADATA = (__name__, __version__, __author__, __copyright__, __license__)

MIN_PYTHON_VERSION = (3, 6)

TARGET_FORMAT_SPACE = ("huawei", "huawei_vrpv8")

TARGET_JUNIPER_ASPATH = ("juniper", "juniper_junos")

SUPPORTED_STRUCTURED_OUTPUT = ("juniper",)

STATUS_CODE_MAP = {"warning": 400, "error": 400, "danger": 500}

DNS_OVER_HTTPS = {
    "google": "https://dns.google/resolve",
    "cloudflare": "https://cloudflare-dns.com/dns-query",
}

PARSED_RESPONSE_FIELDS = (
    ("Prefix", "prefix", "left"),
    ("Active", "active", None),
    ("RPKI State", "rpki_state", "center"),
    ("AS Path", "as_path", "left"),
    ("Next Hop", "next_hop", "left"),
    ("Origin", "source_as", None),
    ("Weight", "weight", "center"),
    ("Local Preference", "local_preference", "center"),
    ("MED", "med", "center"),
    ("Communities", "communities", "center"),
    ("Originator", "source_rid", "right"),
    ("Peer", "peer_rid", "right"),
    ("Age", "age", "right"),
)

SUPPORTED_QUERY_FIELDS = ("query_location", "query_type", "query_target", "query_vrf")
SUPPORTED_QUERY_TYPES = (
    "bgp_route",
    "bgp_community",
    "bgp_aspath",
    "ping",
    "traceroute",
)

FUNC_COLOR_MAP = {
    "primary": "cyan",
    "secondary": "blue",
    "success": "green",
    "warning": "yellow",
    "error": "orange",
    "danger": "red",
}

TRANSPORT_REST = ("frr", "bird")

SCRAPE_HELPERS = {
    "junos": "juniper",
    "ios": "cisco_ios",
    "mikrotik": "mikrotik_routeros",
}

DRIVER_MAP = {
    "arista_eos": "scrapli",
    "cisco_ios": "scrapli",
    "cisco_xe": "scrapli",
    "cisco_xr": "scrapli",
    "cisco_nxos": "scrapli",
    "juniper": "scrapli",
    "frr": "hyperglass_agent",
    "bird": "hyperglass_agent",
}
