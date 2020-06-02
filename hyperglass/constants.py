"""Constant definitions used throughout the application."""

# Standard Library
from datetime import datetime

__name__ = "hyperglass"
__version__ = "1.0.0-beta.34"
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

CREDIT = """
Powered by [**hyperglass**](https://github.com/checktheroads/hyperglass) version \
{version}. Source code licensed \
[_BSD 3-Clause Clear_](https://github.com/checktheroads/hyperglass/blob/master/LICENSE).
"""

DEFAULT_TERMS = """
By using {site_title}, you agree to be bound by the following terms of use:

All queries executed on this page are logged for analysis and troubleshooting. \
Users are prohibited from automating queries, or attempting to process queries in \
bulk. This service is provided on a best effort basis, and {org_name} \
makes no availability or performance warranties or guarantees whatsoever.
"""

DEFAULT_DETAILS = {
    "bgp_aspath": """
{site_title} accepts the following `AS_PATH` regular expression patterns:

| Expression           | Match                                         |
| :------------------- | :-------------------------------------------- |
| `_65000$`            | Originated by 65000                           |
| `^65000_`            | Received from 65000                           |
| `_65000_`            | Via 65000                                     |
| `_65000_65001_`      | Via 65000 and 65001                           |
| `_65000(_.+_)65001$` | Anything from 65001 that passed through 65000 |
""",
    "bgp_community": """
{site_title} makes use of the following BGP communities:

| Community | Description |
| :-------- | :---------- |
| `65000:1` | Example 1   |
| `65000:2` | Example 2   |
| `65000:3` | Example 3   |
""",
    "bgp_route": """
Performs BGP table lookup based on IPv4/IPv6 prefix.
""",
    "ping": """
Sends 5 ICMP echo requests to the target.
""",
    "traceroute": """
Performs UDP Based traceroute to the target. \
For information about how to interpret traceroute results, [click here]\
(https://hyperglass.readthedocs.io/en/latest/assets/traceroute_nanog.pdf).
""",
}

DEFAULT_INFO = {
    "bgp_route": """
---
template: bgp_route
---
Performs BGP table lookup based on IPv4/IPv6 prefix.
""",
    "bgp_community": """
---
template: bgp_community
---
Performs BGP table lookup based on <a href="https://tools.ietf.org/html/rfc4360" target\
="_blank">Extended</a> or <a href="https://tools.ietf.org/html/rfc8195" target=\
"_blank">Large</a> community value.

""",
    "bgp_aspath": """
---
template: bgp_aspath
---
Performs BGP table lookup based on `AS_PATH` regular expression.

""",
    "ping": """
---
template: ping
---
Sends 5 ICMP echo requests to the target.
""",
    "traceroute": """
---
template: traceroute
---
Performs UDP Based traceroute to the target.<br>For information about how to \
interpret traceroute results, <a href="https://hyperglass.readthedocs.io/en/latest/ass\
ets/traceroute_nanog.pdf" target="_blank">click here</a>.
""",
}


DEFAULT_HELP = """
##### BGP Route

Performs BGP table lookup based on IPv4/IPv6 prefix.

---

##### BGP Community

Performs BGP table lookup based on [Extended](https://tools.ietf.org/html/rfc4360) \
or [Large](https://tools.ietf.org/html/rfc8195) community value.

---

##### BGP AS Path

Performs BGP table lookup based on `AS_PATH` regular expression.

---

##### Ping

Sends 5 ICMP echo requests to the target.

---

##### Traceroute

Performs UDP Based traceroute to the target.

For information about how to interpret traceroute results, [click here]\
(https://hyperglass.readthedocs.io/en/latest/assets/traceroute_nanog.pdf).
"""

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
}
