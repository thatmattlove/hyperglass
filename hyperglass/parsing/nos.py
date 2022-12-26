"""Map NOS and Commands to Parsing Functions."""

# Local
from .arista import parse_arista
from .juniper import parse_juniper

structured_parsers = {
    "juniper": {
        "bgp_route": parse_juniper,
        "bgp_aspath": parse_juniper,
        "bgp_community": parse_juniper,
    },
    "arista_eos": {
        "bgp_route": parse_arista,
        "bgp_aspath": parse_arista,
        "bgp_community": parse_arista,
    },
}
