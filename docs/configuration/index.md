# Configuration

Hyperglass configuration files are stored in `hyperglass/hyperglass/configuration/`, in [TOML](https://github.com/toml-lang/toml) format.

```console
hyperglass/configuration/
├── blacklist.toml
├── commands.toml
├── configuration.toml
├── devices.toml
└── requires_ipv6_cidr.toml
```

## Blacklist

Blacklisted querys are defined in `hyperglass/hyperglass/configuration/blacklist.toml`

The blacklist is a simple TOML array (list) of host IPs or prefixes that you do not want end users to be able to query. For example, if you have one or more hosts/subnets you wish to prevent users from looking up (or any contained host or prefix), add them to the list.

#### Example

```toml
blacklist = [
'198.18.0.0/15',
'2001:db8::/32',
'10.0.0.0/8',
'192.168.0.0/16',
'172.16.0.0/12'
]
```

When users attempt to query a matching host/prefix, they will receive the following error message by default:

<img src="/blacklist_error.png" style="width: 70%"></img>

## Commands

Commands are defined in `hyperglass/hyperglass/configuration/commands.toml`. A table for each NOS (Network Operating System) contains three nested tables: `dual`, `ipv4`, and `ipv6`.

| Table     | Function                      | Commands                        |
| --------- | ----------------------------- | ------------------------------- |
| **dual**  | Protocol agnostic commands    | `bgp_community` `bgp_aspath`    |
| **ipv4**  | IPv4-specific commands        | `bgp_route` `ping` `traceroute` |
| **ipv6**  | IPv6-specific commands        | `bgp_route` `ping` `traceroute` |

#### Variables

The following variables can be used in the command definitions.

- `{target}` Maps to search box input.
- `{src_addr_ipv4}` Maps to [src_addr_ipv4](configuration/devices.md/#src_addr_ipv4)
- `{src_addr_ipv6}` Maps to [src_addr_ipv6](configuration/devices.md/#src_addr_ipv6)

#### Example

```toml
[[cisco_ios]]
[cisco_ios.dual]
bgp_community = "show bgp all community {target}"
bgp_aspath = 'show bgp all quote-regexp "{target}"'
[cisco_ios.ipv4]
bgp_route = "show bgp ipv4 unicast {target} | exclude pathid:|Epoch"
ping = "ping {target} repeat 5 source {src_addr_ipv4}"
traceroute = "traceroute {target} timeout 1 probe 2 source {src_addr_ipv4}"
[cisco_ios.ipv6]
bgp_route = "show bgp ipv6 unicast {target} | exclude pathid:|Epoch"
ping = "ping ipv6 {target} repeat 5 source {src_addr_ipv6}"
traceroute = "traceroute ipv6 {target} timeout 1 probe 2 source {src_addr_ipv6}"

[[cisco_xr]]
[cisco_xr.dual]
bgp_community = 'show bgp all unicast community {target} | utility egrep -v "\(BGP |Table |Non-stop\)"'
bgp_aspath = 'show bgp all unicast regexp {target} | utility egrep -v "\(BGP |Table |Non-stop\)"'
[cisco_xr.ipv4]
bgp_route = 'show bgp ipv4 unicast {target} | util egrep "\(BGP routing table entry|Path \#|aggregated by|Origin |Community:|validity| from \)"'
ping = "ping ipv4 {target} count 5 source {src_addr_ipv4}"
traceroute = "traceroute ipv4 {target} timeout 1 probe 2 source {src_addr_ipv4}"
[cisco_xr.ipv6]
bgp_route = 'show bgp ipv6 unicast {target} | util egrep "\(BGP routing table entry|Path \#|aggregated by|Origin |Community:|validity| from \)"'
ping = "ping ipv6 {target} count 5 source {src_addr_ipv6}"
traceroute = "traceroute ipv6 {target} timeout 1 probe 2 source {src_addr_ipv6}"

[[juniper]]
[juniper.dual]
bgp_community = "show route protocol bgp community {target}"
bgp_aspath = "show route protocol bgp aspath-regex {target}"
[juniper.ipv4]
bgp_route = "show route protocol bgp table inet.0 {target} detail"
ping = "ping inet {target} count 5 source {src_addr_ipv4}"
traceroute = "traceroute inet {target} wait 1 source {src_addr_ipv4}"
[juniper.ipv6]
bgp_route = "show route protocol bgp table inet6.0 {target} detail"
ping = "ping inet6 {target} count 5 source {src_addr_ipv6}"
traceroute = "traceroute inet6 {target} wait 1 source {src_addr_ipv6}"
```

## IPv6 CIDR Format Required

Some platforms (namely Cisco IOS) are unable to perform a BGP lookup by IPv6 host address (e.g. 2001:db8::1), but must perform the lookup by prefix (e.g. 2001:db8::/48). `requires_ipv6_cidr.toml` is a list (TOML array) of network operating systems that require this (in Netmiko format).

#### Example

```toml
requires_ipv6_cidr = [
"cisco_ios",
"cisco_nxos"
]
```
