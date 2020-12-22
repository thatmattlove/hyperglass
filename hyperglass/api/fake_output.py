"""Return fake, static data for development purposes."""

# Standard Library
from typing import Dict, Union

PLAIN = r"""
 _                                      _                  
| |__   _   _  _ __    ___  _ __  __ _ | |  __ _  ___  ___ 
| '_ \ | | | || '_ \  / _ \| '__|/ _` || | / _` |/ __|/ __|
| | | || |_| || |_) ||  __/| |  | (_| || || (_| |\__ \\__ \
|_| |_| \__, || .__/  \___||_|   \__, ||_| \__,_||___/|___/
        |___/ |_|                |___/                     

"""  # noqa: W291

ROUTES = [
    {
        "prefix": "198.18.1.0/24",
        "active": True,
        "age": 240,
        "weight": 170,
        "med": 1,
        "local_preference": 100,
        "as_path": [1299, 174, 7018, 7922],
        "communities": ["65000:1", "65000:101", "65000:102", "65000:103"],
        "next_hop": "198.18.0.1",
        "source_as": 7922,
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
        "as_path": [1299, 174, 7018, 7922],
        "communities": ["65000:1", "65000:101", "65000:102", "65000:103"],
        "next_hop": "2001:db8::1",
        "source_as": 7922,
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
        "as_path": [6939, 20115, 20115],
        "communities": [
            "65000:2",
            "65000:201",
            "198.18.0.2:65000",
            "198.18.0.2:650201",
        ],
        "next_hop": "198.18.0.2",
        "source_as": 20115,
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
        "as_path": [6939, 20115, 20115],
        "communities": [
            "65000:2",
            "65000:201",
            "198.18.0.2:65000",
            "198.18.0.2:650201",
        ],
        "next_hop": "2001:db8::2",
        "source_as": 20115,
        "source_rid": "198.18.0.2",
        "peer_rid": "198.18.0.2",
        "rpki_state": 2,
    },
    {
        "prefix": "198.18.3.0/24",
        "active": False,
        "age": 480,
        "weight": 170,
        "med": 3,
        "local_preference": 100,
        "as_path": [22773],
        "communities": ["65000:3"],
        "next_hop": "198.18.0.3",
        "source_as": 22773,
        "source_rid": "198.18.0.3",
        "peer_rid": "198.18.0.3",
        "rpki_state": 3,
    },
    {
        "prefix": "2001:db8:3::/64",
        "active": False,
        "age": 480,
        "weight": 170,
        "med": 3,
        "local_preference": 100,
        "as_path": [22773],
        "communities": ["65000:3"],
        "next_hop": "2001:db8::3",
        "source_as": 22773,
        "source_rid": "198.18.0.3",
        "peer_rid": "198.18.0.3",
        "rpki_state": 3,
    },
    {
        "prefix": "198.18.4.0/24",
        "active": False,
        "age": 480,
        "weight": 170,
        "med": 4,
        "local_preference": 100,
        "as_path": [],
        "communities": ["65000:4"],
        "next_hop": "198.18.0.4",
        "source_as": 209,
        "source_rid": "198.18.0.4",
        "peer_rid": "198.18.0.4",
        "rpki_state": 0,
    },
    {
        "prefix": "2001:db8:4::/64",
        "active": False,
        "age": 480,
        "weight": 170,
        "med": 4,
        "local_preference": 100,
        "as_path": [],
        "communities": ["65000:4"],
        "next_hop": "2001:db8::4",
        "source_as": 209,
        "source_rid": "198.18.0.4",
        "peer_rid": "198.18.0.4",
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
