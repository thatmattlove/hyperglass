"""Map NOS and Commands to Parsing Functions."""

# Project
from hyperglass.parsing.juniper import parse_juniper

nos_parsers = {
    "juniper": {
        "bgp_route": parse_juniper,
        "bgp_aspath": parse_juniper,
        "bgp_community": parse_juniper,
    }
}
