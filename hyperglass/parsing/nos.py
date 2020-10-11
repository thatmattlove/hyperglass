"""Map NOS and Commands to Parsing Functions."""

# Local
from .juniper import parse_juniper
from .mikrotik import parse_mikrotik

structured_parsers = {
    "juniper": {
        "bgp_route": parse_juniper,
        "bgp_aspath": parse_juniper,
        "bgp_community": parse_juniper,
    },
}

scrape_parsers = {
    "mikrotik_routeros": {
        "bgp_route": parse_mikrotik,
        "bgp_aspath": parse_mikrotik,
        "bgp_community": parse_mikrotik,
        "ping": parse_mikrotik,
        "traceroute": parse_mikrotik,
    },
    "mikrotik_switchos": {
        "bgp_route": parse_mikrotik,
        "bgp_aspath": parse_mikrotik,
        "bgp_community": parse_mikrotik,
        "ping": parse_mikrotik,
        "traceroute": parse_mikrotik,
    },
}
