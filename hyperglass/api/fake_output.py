"""Return fake, static data for development purposes."""

# Standard Library
import typing as t

# Project
from hyperglass.models.data import BGPRouteTable

BGP_PLAIN = r"""BGP routing table entry for 4.0.0.0/9, version 1017877672
BGP Bestpath: deterministic-med
Paths: (10 available, best #9, table default)
  Advertised to update-groups:
     50
  1299 3356, (aggregated by 3356 4.69.130.24)
    216.250.230.1 (metric 2000) from 216.250.230.1 (216.250.230.1)
      Origin IGP, metric 0, localpref 100, weight 100, valid, internal, atomic-aggregate
      Community: 1299:25000 14525:0 14525:40 14525:601 14525:1021 14525:2840 14525:3003 14525:4002 14525:9003
  1299 3356, (aggregated by 3356 4.69.130.24), (received-only)
    216.250.230.1 (metric 2000) from 216.250.230.1 (216.250.230.1)
      Origin IGP, metric 0, localpref 150, valid, internal, atomic-aggregate
      Community: 1299:25000 14525:0 14525:40 14525:601 14525:1021 14525:2840 14525:3003 14525:4002 14525:9003
  1299 3356, (aggregated by 3356 4.69.130.184)
    199.34.92.9 (metric 1000) from 199.34.92.9 (199.34.92.9)
      Origin IGP, metric 0, localpref 100, weight 100, valid, internal, atomic-aggregate
      Community: 1299:25000 14525:0 14525:40 14525:601 14525:1021 14525:2840 14525:3001 14525:4001 14525:9003
  1299 3356, (aggregated by 3356 4.69.130.184), (received-only)
    199.34.92.9 (metric 1000) from 199.34.92.9 (199.34.92.9)
      Origin IGP, metric 0, localpref 150, valid, internal, atomic-aggregate
      Community: 1299:25000 14525:0 14525:40 14525:601 14525:1021 14525:2840 14525:3001 14525:4001 14525:9003
  174 3356, (aggregated by 3356 4.69.130.4)
    199.34.92.10 (metric 1000) from 199.34.92.10 (199.34.92.10)
      Origin IGP, metric 0, localpref 100, weight 100, valid, internal, atomic-aggregate
      Community: 174:21000 174:22013 14525:0 14525:40 14525:601 14525:1021 14525:2840 14525:3001 14525:4001 14525:9001
  174 3356, (aggregated by 3356 4.69.130.4), (received-only)
    199.34.92.10 (metric 1000) from 199.34.92.10 (199.34.92.10)
      Origin IGP, metric 0, localpref 150, valid, internal, atomic-aggregate
      Community: 174:21000 174:22013 14525:0 14525:40 14525:601 14525:1021 14525:2840 14525:3001 14525:4001 14525:9001
  209 3356, (aggregated by 3356 4.69.130.2)
    199.34.92.5 (metric 101) from 199.34.92.5 (199.34.92.5)
      Origin IGP, metric 8006570, localpref 150, weight 200, valid, internal, atomic-aggregate
      Community: 209:88 209:888 3356:0 3356:3 3356:100 3356:123 3356:575 3356:2011 14525:0 14525:40 14525:1021 14525:2840 14525:3002 14525:4003 14525:9005
  209 3356, (aggregated by 3356 4.69.130.2), (received-only)
    199.34.92.5 (metric 101) from 199.34.92.5 (199.34.92.5)
      Origin IGP, metric 8006570, localpref 150, valid, internal, atomic-aggregate
      Community: 209:88 209:888 3356:0 3356:3 3356:100 3356:123 3356:575 3356:2011 14525:0 14525:40 14525:1021 14525:2840 14525:3002 14525:4003 14525:9005
  6939 3356, (aggregated by 3356 4.69.130.4)
    184.105.247.177 from 184.105.247.177 (216.218.252.234)
      Origin IGP, localpref 150, weight 200, valid, external, atomic-aggregate, best
      Community: 6939:7016 6939:8840 6939:9001 14525:0 14525:40 14525:1021 14525:2840 14525:3002 14525:4003 14525:9002
  6939 3356, (aggregated by 3356 4.69.130.4), (received-only)
    184.105.247.177 from 184.105.247.177 (216.218.252.234)
      Origin IGP, localpref 100, valid, external, atomic-aggregate
      Community: 6939:7016 6939:8840 6939:9001
"""  # noqa: W291,E501

BGP_ROUTES = [
    {
        "prefix": "1.1.1.0/24",
        "active": True,
        "age": 1025337,
        "weight": 170,
        "med": 0,
        "local_preference": 175,
        "as_path": [1299, 13335],
        "communities": [
            "1299:35000",
            "14525:0",
            "14525:41",
            "14525:600",
            "14525:1021",
            "14525:2840",
            "14525:3001",
            "14525:4001",
            "14525:9003",
        ],
        "next_hop": "62.115.189.136",
        "source_as": 13335,
        "source_rid": "141.101.72.1",
        "peer_rid": "2.255.254.43",
        "rpki_state": 1,
    },
    {
        "prefix": "1.1.1.0/24",
        "active": False,
        "age": 1584622,
        "weight": 200,
        "med": 0,
        "local_preference": 250,
        "as_path": [13335],
        "communities": [
            "14525:0",
            "14525:20",
            "14525:600",
            "14525:1021",
            "14525:2840",
            "14525:3002",
            "14525:4003",
            "14525:9009",
        ],
        "next_hop": "",
        "source_as": 13335,
        "source_rid": "172.68.129.1",
        "peer_rid": "199.34.92.5",
        "rpki_state": 3,
    },
    {
        "prefix": "1.1.1.0/24",
        "active": False,
        "age": 982517,
        "weight": 200,
        "med": 0,
        "local_preference": 250,
        "as_path": [13335],
        "communities": [
            "14525:0",
            "14525:20",
            "14525:600",
            "14525:1021",
            "14525:2840",
            "14525:3002",
            "14525:4003",
            "14525:9009",
        ],
        "next_hop": "",
        "source_as": 13335,
        "source_rid": "172.68.129.1",
        "peer_rid": "199.34.92.6",
        "rpki_state": 3,
    },
    {
        "prefix": "1.1.1.0/24",
        "active": False,
        "age": 1000101,
        "weight": 200,
        "med": 0,
        "local_preference": 250,
        "as_path": [13335],
        "communities": [
            "13335:10014",
            "13335:19000",
            "13335:20050",
            "13335:20500",
            "13335:20530",
            "14525:0",
            "14525:20",
            "14525:600",
            "14525:1021",
            "14525:2840",
            "14525:3003",
            "14525:4002",
            "14525:9009",
        ],
        "next_hop": "",
        "source_as": 13335,
        "source_rid": "141.101.73.1",
        "peer_rid": "216.250.230.2",
        "rpki_state": 3,
    },
]

PING = r"""PING 1.1.1.1 (1.1.1.1): 56 data bytes
64 bytes from 1.1.1.1: icmp_seq=0 ttl=59 time=4.696 ms
64 bytes from 1.1.1.1: icmp_seq=1 ttl=59 time=4.699 ms
64 bytes from 1.1.1.1: icmp_seq=2 ttl=59 time=4.640 ms
64 bytes from 1.1.1.1: icmp_seq=3 ttl=59 time=4.583 ms
64 bytes from 1.1.1.1: icmp_seq=4 ttl=59 time=4.640 ms

--- 1.1.1.1 ping statistics ---
5 packets transmitted, 5 packets received, 0% packet loss
round-trip min/avg/max/stddev = 4.583/4.652/4.699/0.043 ms
"""

TRACEROUTE = r"""traceroute to 1.1.1.1 (1.1.1.1), 30 hops max, 52 byte packets
 1  157.231.183.50  4.412 ms
 2  129.219.10.4  4.612 ms
 3  128.249.9.12  4.503 ms
 4  139.15.19.3  7.458 ms
 5  172.69.68.3  4.814 ms
 6  1.1.1.1  4.564 ms
"""


async def fake_output(query_type: str, structured: bool) -> t.Union[str, BGPRouteTable]:
    """Bypass the standard execution process and return static, fake output."""

    if "ping" in query_type:
        return PING
    if "traceroute" in query_type:
        return TRACEROUTE
    if "bgp" in query_type:
        if structured:
            return BGPRouteTable(
                vrf="default",
                count=len(BGP_ROUTES),
                routes=BGP_ROUTES,
                winning_weight="high",
            )
        return BGP_PLAIN
    return BGP_PLAIN
