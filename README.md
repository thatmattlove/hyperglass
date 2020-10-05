<div align="center">
  <br/>
  <img src="https://res.cloudinary.com/hyperglass/image/upload/v1593916013/logo.svg" width=300></img>
  <br/>
  <h3>The network looking glass that tries to make the internet better.</h3>
  <br/>  
  A looking glass is implemented by network operators as a way of providing customers, peers, or the general public with a way to easily view elements of, or run tests from the provider's network.
</div>

<hr/>

<div align="center">

[**Documentation**](https://hyperglass.io)&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;[**Screenshots**](https://hyperglass.io/screenshots)&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;[**Live Demo**](https://hyperglass.io/demo)

[![PyPI](https://img.shields.io/pypi/v/hyperglass?style=for-the-badge)](https://pypi.org/project/hyperglass/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/hyperglass?color=%2340798C&style=for-the-badge)
[![CI](https://img.shields.io/travis/com/checktheroads/hyperglass/v1.0.0?style=for-the-badge)](https://travis-ci.com/github/checktheroads/hyperglass)

[![GitHub Contributors](https://img.shields.io/github/contributors/checktheroads/hyperglass?color=40798C&style=for-the-badge)](https://github.com/checktheroads/hyperglass)
[![Gitter](https://img.shields.io/gitter/room/checktheroads/hyperglass?color=ff5e5b&style=for-the-badge)](https://gitter.im/hyperglass)
[![Telegram](https://img.shields.io/badge/chat-telegram-blue?style=for-the-badge&color=blue&logo=telegram)](https://t.me/hyperglasslg)

<br/>

hyperglass is intended to make implementing a looking glass too easy not to do, with the lofty goal of improving the internet community at large by making looking glasses more common across autonomous systems of any size.

<br/>

⚠️ **v1.0.0** *is currently in beta. While everything should work, some things might not. Documentation and the live demo are not yet complete. For a fully working and documented version of hyperglass, **please go to the [v0 branch](https://github.com/checktheroads/hyperglass/tree/v0)**.*

</div>

### [Changelog](https://github.com/checktheroads/hyperglass/blob/v1.0.0/CHANGELOG.md)

## Features

- BGP Route, BGP Community, BGP AS Path, Ping, & Traceroute
- Full IPv6 support
- Customizable everything: features, theme, UI/API text, error messages, commands
- Built in support for:
    - Cisco IOS/IOS-XE
    - Cisco NX-OS
    - Cisco IOS-XR
    - Juniper JunOS
    - Arista EOS
    - Huawei
    - Mikrotik
    - VyOS
    - FRRouting
    - BIRD
- Configurable support for any other [supported platform](https://hyperglass.io/docs/platforms)
- Optionally access devices via an SSH proxy/jump server
- VRF support
- Access List/prefix-list style query control to whitelist or blacklist query targets on a per-VRF basis
- REST API with automatic, configurable OpenAPI documentation
- Modern, responsive UI built on [ReactJS](https://reactjs.org/), with [NextJS](https://nextjs.org/) & [Chakra UI](https://chakra-ui.com/)
- Query multiple devices simultaneously
- Browser-based DNS-over-HTTPS resolution of FQDN queries

*To request support for a specific platform, please [submit a Github Issue](https://github.com/checktheroads/hyperglass/issues/new) with the **enhancement** label.*

### [Get Started →](https://hyperglass.io/)

## Community

- [Telegram](https://t.me/hyperglasslg)
- [Gitter](https://gitter.im/hyperglass)
- [Twitter](https://twitter.com/checktheroads)
- [Keybase](https://keybase.io/team/hyperglass)

Any users, potential users, or contributors of hyperglass are welcome to join and discuss usage, feature requests, bugs, and other things.

**hyperglass is developed with the express intention of being free to the networking community**.

*However, the hyperglass demo does cost [@checktheroads](https://github.com/checktheroads) about $15/month for 3 Digital Ocean droplets, and $60/year for the [hyperglass.io](https://hyperglass.io) domain. If you're feeling particularly helpful and want to help offset that cost, small donations are welcome.*

[![Donate](https://img.shields.io/badge/Donate-blue.svg?logo=paypal&style=for-the-badge)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ZQFH3BB2B5M3E&source=url)

## License

[Clear BSD License](https://github.com/checktheroads/hyperglass/v1.0.0/LICENSE)
