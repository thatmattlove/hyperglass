Commands are defined in `hyperglass/hyperglass/config/commands.toml`. Formatted as a nested array of tables, each table defines the commands that will be used to execute the queries on the routers.

Each table contains three nested tables:

##### dual

Commands that are IP protocol agnostic:

- `bgp_community`
- `bgp_aspath`

##### ipv4

Commands that are IPv4-specific:

- `bgp_route`
- `ping`
- `traceroute`

##### ipv6

Commands that are IPv6-specific:

- `bgp_route`
- `ping`
- `traceroute`

#### Default Configuration

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

Every attempt has been made to filter out as much "noise" as possible from the command output.

##### `{target}`

Maps to search box input.

##### `{src_addr_ipv4}`

Maps to [src_addr_ipv4](configuration/devices.md/#src_addr_ipv4)

##### `{src_addr_ipv6}`

Maps to [src_addr_ipv6](configuration/devices.md/#src_addr_ipv6)
