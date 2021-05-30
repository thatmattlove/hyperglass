"""Constant store for large default values."""

CREDIT = """
Powered by [**hyperglass**](https://hyperglass.io) version {version}. \
Source code licensed [_BSD 3-Clause Clear_](https://hyperglass.io/docs/license/).
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
(https://hyperglass.io/traceroute_nanog.pdf).
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
(https://hyperglass.io/traceroute_nanog.pdf).
"""
