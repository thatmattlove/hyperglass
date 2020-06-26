<div align="center">

<img src="logo.png" width=300></img>

# ⚡️ [1.0 Beta Release](https://github.com/checktheroads/hyperglass/tree/v1.0.0)
I've been hard at work on a revamp of hyperglass since its initial release in June 2019, and I'm pleased to make version 1.0.0 available for beta testing. While I feel v1.0.0 is actually _more_ stable than the original release here in the master branch, I have not had time to complete a few lingering UI features, documentation, screenshots, an updated demo site, contributor guidelines, and testing.

**I invite any current or new users of hyperglass to try out the [1.0 beta release](https://github.com/checktheroads/hyperglass/tree/v1.0.0) or look over the [documentation](https://hyperglass.io), and let me know of any issues to address prior to merging it to the master branch.**

<hr>

hyperglass is a modern network looking glass application. A looking glass is typically implemented by network service providers as a way of providing customers, peers, and partners with a way to easily view elements of, or run tests from the provider's network. 

<hr>

</div>

<div align="center">

[**Documentation**](https://hyperglass.readthedocs.io)&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;[**Screenshots**](https://hyperglass.readthedocs.io/en/latest/screenshots/)&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;[**Live Demo**](https://hyperglass.allroads.io/)

[![Build Status](https://travis-ci.org/checktheroads/hyperglass.svg?branch=master)](https://travis-ci.org/checktheroads/hyperglass)
![GitHub issues](https://img.shields.io/github/issues/checktheroads/hyperglass.svg)
![Pylint](https://raw.githubusercontent.com/checktheroads/hyperglass/master/pylint.svg?sanitize=true)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

</div>

## Features

-   BGP Route, BGP Community, BGP AS Path, Ping, Traceroute
-   Full frontend and backend IPv6 support
-   [Netmiko](https://github.com/ktbyers/netmiko)-based connection handling for traditional network devices
-   [FRRouting](https://frrouting.org/) support via [hyperglass-frr](https://github.com/checktheroads/hyperglass-frr) REST API
-   [BIRD](https://bird.network.cz/) support via [hyperglass-bird](https://github.com/checktheroads/hyperglass-bird) REST API
-   Customizable commands for each query type by vendor
-   Clean, modern, google-esq GUI based on the [Bumla](https://bulma.io) framework
-   Customizable colors, logo, web fonts, error messages, UI text
-   Simple TOML config file for all customizable parameters (no databases!)
-   Optional SSH Proxy to further direct secure router access
-   Configurable IP/Prefix "blacklist" to prevent lookup of sensitive prefixes
-   Configurable rate limiting, powered by [Flask-Limiter](https://github.com/alisaifee/flask-limiter)
-   Query response caching with configurable cache timeout
-   [Prometheus](https://prometheus.io/) metrics for query statistics tracking ([Check out the live demo!](https://hyperglass.allroads.io/grafana))

## Platform Support

hyperglass is preconfigured to support the following platforms:

-   **Cisco IOS-XR**: Netmiko `cisco_xr` vendor class
-   **Cisco Classic IOS/IOS-XE**: Netmiko `cisco_ios` vendor class
-   **Juniper JunOS**: Netmiko `junos` vendor class
-   **FRRouting**: [`hyperglass-frr`](https://github.com/checktheroads/hyperglass-frr) API
-   **BIRD**: [`hyperglass-bird`](https://github.com/checktheroads/hyperglass-bird) API

Theoretically, any vendor supported by Netmiko can be supported by hyperglass. To request support for a specifc platform, please [submit a Github Issue](https://github.com/checktheroads/hyperglass/issues/new) with the **enhancement** label.

hyperglass is intended to make implementing a looking glass too easy not to do, with the lofty goal of improving the internet community at large by making looking glasses more common across autonomous systems of any size.

### [Get Started →](https://hyperglass.readthedocs.io/)

## Community

- [Gitter](https://gitter.im/hyperglass)
- [Keybase](https://keybase.io/team/hyperglass)
- [Twitter](https://twitter.com/checktheroads)

Any users, potential users, or contributors of hyperglass are welcome to join and discuss usage, feature requests, bugs, and other things.

**hyperglass is developed with the express intention of being free to the networking community**.

*However, the hyperglass demo does cost [@checktheroads](https://github.com/checktheroads) about $15/month for 3 Digital Ocean droplets, and $60/year for the [hyperglass.io](https://hyperglass.io) domain. If you're feeling particularly helpful and want to help offset that cost, small donations are welcome.*

[![Donate](https://img.shields.io/badge/Donate-blue.svg?logo=paypal)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ZQFH3BB2B5M3E&source=url)

## License

[Clear BSD License](https://github.com/checktheroads/hyperglass/blob/master/LICENSE)
