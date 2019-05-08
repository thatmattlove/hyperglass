<img src="hyperglass/static/images/hyperglass-dark.png" width=300></img>

**Hyperglass** is a network looking glass application. A looking glass is typically implemented by network service providers as a way of providing customers, peers, and partners with a way to easily view elements of, or run tests from the provider's network.

<br>

![GitHub issues](https://img.shields.io/github/issues/checktheroads/hyperglass.svg)
![GitHub](https://img.shields.io/github/license/checktheroads/hyperglass.svg)
![GitHub top language](https://img.shields.io/github/languages/top/checktheroads/hyperglass.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Features

-   BGP Route, BGP Community, BGP AS_PATH, Ping, Traceroute
-   Full IPv6 support
-   [Netmiko](https://github.com/ktbyers/netmiko)-based connection handling
-   Customizable commands for each function by vendor
-   Clean, google-esq GUI based on the [Bumla](https://bulma.io) framework
-   Customizable colors, logo, web fonts, error messages, UI text
-   TOML-based config file for all customizable parameters (no databases!)
-   Configurable IP/Prefix "blacklist" to prevent lookup of internal/private prefixes
-   Configurable rate limiting, powered by [Flask-Limiter](https://github.com/alisaifee/flask-limiter)
-   Query response caching with configurable cache timeout, powered by [Flask-Caching](https://github.com/sh4nks/flask-caching)

## Documentation

Documentation can be found [here](https://hyperglass.readthedocs.io), or in the `docs/` directory.

## Preview

For screenshots, see [here](screenshots.md), or the `screenshots/` directory.

## Platform Support

Theoretically, any vendor supported by Netmiko can be supported by Hyperglass. However, I am currently listing platforms I have personally tested and verified full functionality with:

### Routers

-   Cisco IOS-XR: `cisco_xr`
-   Cisco Classic IOS/IOS-XE: `cisco_ios`
-   Juniper JunOS: `junos`

### Proxies

-   Linux: `linux_ssh`

## Acknowledgements

-   This project originally started as a fork of vraulsan's [looking-glass](https://github.com/vraulsan/looking-glass) project. The guts of the Flask components still remain from that project, but almost everything else has been rewritten. Nevertheless, the inspiration for building hyperglass came from here.

## License

[Clear BSD License](https://github.com/checktheroads/hyperglass/master/LICENSE)
