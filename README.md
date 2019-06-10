<img src="hyperglass/static/images/hyperglass-dark.png" width=300></img>

**hyperglass** is a modern network looking glass application. A looking glass is typically implemented by network service providers as a way of providing customers, peers, and partners with a way to easily view elements of, or run tests from the provider's network.

**hyperglass** is intended to make implementing a looking glass too easy not to do, with the big-picture goal of improving the internet community as a whole by making looking glasses more common across autonomous systems of any size.

<br>

![GitHub issues](https://img.shields.io/github/issues/checktheroads/hyperglass.svg)
![GitHub](https://img.shields.io/github/license/checktheroads/hyperglass.svg)
![GitHub top language](https://img.shields.io/github/languages/top/checktheroads/hyperglass.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Features

-   BGP Route, BGP Community, BGP AS Path, Ping, Traceroute
-   Full IPv6 support
-   [Netmiko](https://github.com/ktbyers/netmiko)-based connection handling for traditional network devices
-   [FRRouting](https://frrouting.org/) support via [hyperglass-frr](https://github.com/checktheroads/hyperglass-frr) REST API
-   Customizable commands for each query type by vendor
-   Clean, modern, google-esq GUI based on the [Bumla](https://bulma.io) framework
-   Customizable colors, logo, web fonts, error messages, UI text
-   Simple TOML config file for all customizable parameters (no databases!)
-   Optional SSH Proxy to further direct secure router access
-   Configurable IP/Prefix "blacklist" to prevent lookup of sensitive prefixes
-   Configurable rate limiting, powered by [Flask-Limiter](https://github.com/alisaifee/flask-limiter)
-   Query response caching with configurable cache timeout, powered by [Flask-Caching](https://github.com/sh4nks/flask-caching)
-   [Prometheus](https://prometheus.io/) metrics for query statistics tracking

## Documentation

Documentation can be found [here](https://hyperglass.readthedocs.io), or in the `docs/` directory.

## Preview

For screenshots, see [here](screenshots.md), or the `screenshots/` directory.

## Platform Support

Theoretically, any vendor supported by Netmiko can be supported by hyperglass. However, hyperglass is preconfigured to support the following platforms:

### Routers

-   Cisco IOS-XR: Netmiko `cisco_xr` vendor class
-   Cisco Classic IOS/IOS-XE: Netmiko `cisco_ios` vendor class
-   Juniper JunOS: Netmiko `junos` vendor class
-   FRRouting: hyperglass-frr API

### Proxies

-   Linux: `linux_ssh`

## Acknowledgements

-   This project originally started as a fork of [vraulsan](https://github.com/vraulsan)'s [looking-glass](https://github.com/vraulsan/looking-glass) project. The guts of the Flask components still remain from that project, but almost everything else has been rewritten. Nevertheless, the inspiration for building hyperglass came from here.

## License

[Clear BSD License](https://github.com/checktheroads/hyperglass/master/LICENSE)
