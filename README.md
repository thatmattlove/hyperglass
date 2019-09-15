<img src="logo.png" width=300></img>

**hyperglass** is a modern network looking glass application. A looking glass is typically implemented by network service providers as a way of providing customers, peers, and partners with a way to easily view elements of, or run tests from the provider's network.

<hr>

<div align="center">

[**Documentation**](https://hyperglass.readthedocs.io)&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;[**Screenshots**](https://hyperglass.readthedocs.io/en/latest/screenshots/)&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;[**Live Demo**](https://hyperglass.allroads.io/)

[![Build Status](https://travis-ci.org/checktheroads/hyperglass.svg?branch=master)](https://travis-ci.org/checktheroads/hyperglass)
![GitHub issues](https://img.shields.io/github/issues/checktheroads/hyperglass.svg)
![Pylint](https://raw.githubusercontent.com/checktheroads/hyperglass/master/pylint.svg?sanitize=true)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

</div>

<hr>

**hyperglass** is intended to make implementing a looking glass too easy not to do, with the lofty goal of improving the internet community at large by making looking glasses more common across autonomous systems of any size.

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

## Coming Soon

-   [GoBGP](https://github.com/osrg/gobgp) Support

## Community

There is now a [hyperglass team](https://keybase.io/team/hyperglass) on [Keybase](https://keybase.io/)! Any users, potential users, or contributors of hyperglass are welcome to join to discuss usage, feature requests, bugs, and other things.

**hyperglass is developed with the express intention of being free to the networking community**.

*However, the hyperglass demo does cost [@checktheroads](https://github.com/checktheroads) about $15/month for 3 Digital Ocean droplets. If you're feeling particularly helpful and want to help offset that cost, small donations are welcome.*

[![Donate](https://img.shields.io/badge/Donate-blue.svg?logo=paypal)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ZQFH3BB2B5M3E&source=url)

## Acknowledgements

-   This project originally started as a fork of [vraulsan](https://github.com/vraulsan)'s [looking-glass](https://github.com/vraulsan/looking-glass) project. The guts of the Flask components still remain from that project, but almost everything else has been rewritten. Nevertheless, the inspiration for building hyperglass came from here.

## License

[Clear BSD License](https://github.com/checktheroads/hyperglass/blob/master/LICENSE)

# *Development Status*

Beginning 2019-09-01, the *initial* release of **hyperglass** will only receive updates for critical bug fixes or vulnerabilities. Any enhancements, new features, or other general improvements will, if accepted/approved, be implemented in version 1.0.0, development for which can be tracked via the [v1.0.0 branch](https://github.com/checktheroads/hyperglass/tree/v1.0.0).

## But why

The initial release of hyperglass was the culmination of my first ever foray into development, so naturally it is not perfect. Building that initial release was an incredibly fun process through which I learned a *lot*, and the community's feedback has been overwhelmingly positive. However, after the initial release I still had a massive list of features I wanted to try to implement. As I began that process, I found many aspects of the hyperglass backend that needed improving (or in some cases, significant overhaul). So, I decided to put all my efforts into a single "1.0" release and treat the initial hyperglass release as more of a beta. This way, I'm able to dedicate what little development time I have to the drastic improvements in the works in the v1.0.0 branch.

## What's coming in 1.0?

##### So far, I've already implemented the following:

:heavy_check_mark: [Asyncio](https://docs.python.org/3/library/asyncio.html) end-to-end wherever possible

:heavy_check_mark: Migrated web framework from Flask to [Sanic](https://github.com/huge-success/sanic) (removes Gunicorn dependency)

:heavy_check_mark: Migrated outbound http client framework from Requests to [HTTPX](https://github.com/encode/httpx) for FRR/BIRD connections

:heavy_check_mark: Migrated front-end framework from Bulma to [Bootstrap 4](https://getbootstrap.com/) using a custom theme, for which most visual aspects are still completely customizable.

:heavy_check_mark: Front-end frameworks/dependencies are no longer bundled with hyperglass. [Yarn](https://yarnpkg.com/lang/en/) now handles package management, and [ParcelJS](https://parceljs.org/) now bundles and minifies all Javascript libraries, CSS frameworks and custom CSS, fonts, etc. making for a more consistent and controlable user experience.

:heavy_check_mark: Migrated config file language from TOML to [YAML](https://en.wikipedia.org/wiki/YAML).

:heavy_check_mark: [Pydantic](https://github.com/samuelcolvin/pydantic/) for config file modeling and validation. This will reduce, if not remove, the likelihood of accidentally misconfiguring hyperglass, your devices, or custom commands. It also allows for a significantly more sensible way of setting reasonable defaults, which now exist for all configuration variables, except for devices.

:heavy_check_mark: Ability to query multiple devices at once.

:heavy_check_mark: Custom commands are no longer NOS-specific. Command "profiles" can be arbitrarily created and associated with any device. This means that even if two different devices are running `cisco_ios`, one device can use one set of commands, and the other device can use a different set of commands.

:heavy_check_mark: Some other backend goodies like: A (configurable) global timeout, so if a device can't be reached for whatever reason, the user is not left to watch a loading bar. Faster SSH queries. *Way* faster queries when using an SSH proxy/tunnel. Drastically improved error handling with 100% customizable user-facing error messages. Front-end to back-end communication is now 100% JSON, which means hyperglass is also a looking glass API for your network, not just a GUI.

##### What I'm still working on:

:white_check_mark: VRF support. You'll be able to, per-device, enable queries to be VRF and AFI specific.

:white_check_mark: *Possibly* move to [Netdev](https://github.com/selfuryon/netdev) instead of Netmiko for SSH connection handling for performance gains.

:white_check_mark: Improved native Juniper support

:white_check_mark: Native Arista support

:white_check_mark: Native Huawei support

:white_check_mark: Improved reverse proxy docs, mainly for adding GZIP compression support for static files

:white_check_mark: Make Grafana dashboard available via Grafana's plugin marketplace

...and several other things that probably won't make it into 1.0 :)
