"""Return fake, static data for development purposes."""

# Standard Library
from typing import Dict, Union

PLAIN = r""" # noqa: W291
 _                                      _                  
| |__   _   _  _ __    ___  _ __  __ _ | |  __ _  ___  ___ 
| '_ \ | | | || '_ \  / _ \| '__|/ _` || | / _` |/ __|/ __|
| | | || |_| || |_) ||  __/| |  | (_| || || (_| |\__ \\__ \
|_| |_| \__, || .__/  \___||_|   \__, ||_| \__,_||___/|___/
        |___/ |_|                |___/                     

"""

ROUTES = [
    {
        "prefix": "198.18.1.0/24",
        "active": True,
        "age": 240,
        "weight": 170,
        "med": 1,
        "local_preference": 100,
        "as_path": [65001],
        "communities": ["65000:1"],
        "next_hop": "198.18.0.1",
        "source_as": 65001,
        "source_rid": "198.18.0.1",
        "peer_rid": "198.18.0.1",
        "rpki_state": 1,
    },
    {
        "prefix": "2001:db8:1::/64",
        "active": True,
        "age": 240,
        "weight": 170,
        "med": 1,
        "local_preference": 100,
        "as_path": [65001],
        "communities": ["65000:1"],
        "next_hop": "2001:db8::1",
        "source_as": 65001,
        "source_rid": "198.18.0.1",
        "peer_rid": "198.18.0.1",
        "rpki_state": 1,
    },
    {
        "prefix": "198.18.2.0/24",
        "active": False,
        "age": 480,
        "weight": 170,
        "med": 2,
        "local_preference": 100,
        "as_path": [65002],
        "communities": ["65000:2"],
        "next_hop": "198.18.0.2",
        "source_as": 65002,
        "source_rid": "198.18.0.2",
        "peer_rid": "198.18.0.2",
        "rpki_state": 2,
    },
    {
        "prefix": "2001:db8:2::/64",
        "active": False,
        "age": 480,
        "weight": 170,
        "med": 2,
        "local_preference": 100,
        "as_path": [65002],
        "communities": ["65000:2"],
        "next_hop": "2001:db8::2",
        "source_as": 65002,
        "source_rid": "198.18.0.2",
        "peer_rid": "198.18.0.2",
        "rpki_state": 2,
    },
    {
        "prefix": "198.18.3.0/24",
        "active": False,
        "age": 480,
        "weight": 170,
        "med": 2,
        "local_preference": 100,
        "as_path": [65003],
        "communities": ["65000:3"],
        "next_hop": "198.18.0.3",
        "source_as": 65003,
        "source_rid": "198.18.0.3",
        "peer_rid": "198.18.0.3",
        "rpki_state": 0,
    },
    {
        "prefix": "2001:db8:3::/64",
        "active": False,
        "age": 480,
        "weight": 170,
        "med": 2,
        "local_preference": 100,
        "as_path": [65003],
        "communities": ["65000:3"],
        "next_hop": "2001:db8::3",
        "source_as": 65003,
        "source_rid": "198.18.0.3",
        "peer_rid": "198.18.0.3",
        "rpki_state": 0,
    },
]

STRUCTURED = {
    "vrf": "default",
    "count": len(ROUTES),
    "routes": ROUTES,
    "winning_weight": "high",
}


async def fake_output(structured: bool) -> Union[str, Dict]:
    """Bypass the standard execution process and return static, fake output."""
    output = PLAIN

    if structured:
        output = STRUCTURED

    return output
