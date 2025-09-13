"### Install https://hyperglass.dev/installation/docker"

mkdir -p /etc/hyperglass/svg

cd /opt

git clone https://github.com/CarlosSuporteISP/hyperglass_structured.git --depth=1

mv hyperglass_structured hyperglass

cd /opt/hyperglass

"### https://hyperglass.dev/configuration/overview"

"### https://hyperglass.dev/configuration/config Change the files in the /etc/hyperglass folder after copying with your information or add something following the official doc"

cp /opt/hyperglass/.samples/sample_config /etc/hyperglass/config.yaml

cp /opt/hyperglass/.samples/sample_terms-and-conditions /etc/hyperglass/terms-and-conditions.md

"### https://hyperglass.dev/configuration/devices Change the files in the /etc/hyperglass folder after copying with your information or add something following the official doc"

cp /opt/hyperglass/.samples/sample_devices2 /etc/hyperglass/devices.yaml

"### https://hyperglass.dev/configuration/directives Change the files in the /etc/hyperglass folder after copying with your information or add something following the official doc"

cp /opt/hyperglass/.samples/sample_directives_huawei /etc/hyperglass/directives.yaml

cp /opt/hyperglass/.samples/sample_directives_juniper /etc/hyperglass/directives.yaml

cp /opt/hyperglass/.samples/sample_directives_mikrotik /etc/hyperglass/directives.yaml

"### Environment Variables https://hyperglass.dev/installation/environment-variables"

cp /opt/hyperglass/.samples/sample_hyperglass /etc/hyperglass/hyperglass.env


"###"

You also need to add your AS prefixes to deny queries if you don't want others to look up your own prefixes from your hyperglass instance.

In the directives file, there is a field that is usually commented out. This configuration is meant for devices like Huawei or MikroTik, but it is currently still using the default option from the directives. From what I've tested, putting the rules in the configuration folder (/etc/hyperglass/...) didn't work. If it works later, we can do everything within the directives file in /etc/hyperglass, but for now, it's okay to use the default.

It's possible to create or use the ENTRYPOINT in the Dockerfile to change this at build time when starting the service, but I don't have time right now to stop and implement this.

The code snippet, originally commented, should be modified to something like this: /opt/hyperglass/hyperglass/defaults/directives/huawei.py | /opt/hyperglass_structured/hyperglass/defaults/directives/mikrotik.py

         # DENY RULE FOR AS PREFIX - IPv4
         RuleWithIPv4(
            condition="172.16.0.0/22",
            ge="22",
            le="32",
            action="deny",
            command="",
        ),

        # DENY RULE FOR AS PREFIX - IPv6
        RuleWithIPv6(
            condition="fd00:2::/32",
            ge="32",
            le="128",
            action="deny",
            command="",
        ),

mikrotik v6

command="ip route print detail without-paging where {target} in dst-address bgp and dst-address !=0.0.0.0/0",
command="ipv6 route print detail without-paging where {target} in dst-address bgp and dst-address !=::/0",

mikrotik v7

command="routing route print detail without-paging where {target} in dst-address bgp and dst-address !=0.0.0.0/0",
command="routing route print detail without-paging where {target} in dst-address bgp and dst-address !=::/0",



"###"

"### Optional: Quickstart"

cd /opt/hyperglass

docker compose up

"### Create a systemd service"

cp /opt/hyperglass/.samples/hyperglass-docker.service /etc/hyperglass/hyperglass.service

ln -s /etc/hyperglass/hyperglass.service /etc/systemd/system/hyperglass.service

systemctl daemon-reload

systemctl enable hyperglass

systemctl start hyperglass



"###"

 Acknowledgments:

    To thatmatt for this incredible project that I really like. Nothing against other Looking Glass (LG) projects. https://github.com/thatmattlove/hyperglass

    To remotti for the tips on Telegram, his attention, and for his fork https://github.com/remontti/hyperglass/tree/main, https://blog.remontti.com.br/7201, which is already quite deprecated due to its age (Node 14, etc.) and not being in Docker. This is why I decided to move to the official version.

    To the user \邪萬教教我/ @Yukaphoenix572 好呆. Thanks to a message from him in the Telegram group, my mind was opened to the solution after I searched through the conversations.

    To issue https://github.com/thatmattlove/hyperglass/issues/318 for the solution to queries that also weren't working on Tik-Tik (for those who use Claro).

    And of course, last but not least: to AIs. My apologies to those who don't like the "code vibe," but they help a lot. I used many of the six main AIs on the market, but only Manus truly managed to help me, contributing about 45% of the development, testing, adjustments, and descriptions.

The total development time took over three weeks to get everything adjusted. Yes, I know I'm not that great at development, but I'm studying and improving. As I always say, in life and professionally, we always have something to learn; we never know everything.

I also adjusted the official plugin (which wasn't working) for Huawei.

The issue was the format in which the prefix was being passed to the device. Huawei expects the format 192.0.2.0 24 (with a space), but the official plugin was sending it in the 192.0.2.0/24 format (with a slash).

The fix was made to adapt to the format that Huawei accepts for queries.



"###"


<div align="center">
  <br/>
  <img src="https://res.cloudinary.com/hyperglass/image/upload/v1593916013/logo-light.svg" width=300></img>
  <br/>
  <h3>The network looking glass that tries to make the internet better.</h3>
  <br/>  
  A looking glass is implemented by network operators as a way of providing customers, peers, or the general public with a way to easily view elements of, or run tests from the provider's network.
</div>

<hr/>

<div align="center">

[**Documentation**](https://hyperglass.dev)&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;[**Live Demo**](https://demo.hyperglass.dev/)

[![Frontend Tests](https://img.shields.io/github/actions/workflow/status/thatmattlove/hyperglass/frontend.yml?label=Frontend%20Tests&style=for-the-badge)](https://github.com/thatmattlove/hyperglass/actions/workflows/frontend.yml)
[![Backend Tests](https://img.shields.io/github/actions/workflow/status/thatmattlove/hyperglass/backend.yml?label=Backend%20Tests&style=for-the-badge)](https://github.com/thatmattlove/hyperglass/actions/workflows/backend.yml)

<br/>

hyperglass is intended to make implementing a looking glass too easy not to do, with the lofty goal of improving the internet community at large by making looking glasses more common across autonomous systems of any size.

</div>

### [Changelog](https://hyperglass.dev/changelog)

## Features

- BGP Route, BGP Community, BGP AS Path, Ping, & Traceroute, or [add your own commands](https://hyperglass.dev/configuration/directives).
- Full IPv6 support
- Customizable everything: features, theme, UI/API text, error messages, commands
- Built-in support for:
  - Arista EOS
  - BIRD
  - Cisco IOS
  - Cisco NX-OS
  - Cisco IOS-XR
  - FRRouting
  - Huawei VRP
  - Juniper Junos
  - Mikrotik
  - Nokia SR OS
  - OpenBGPD
  - TNSR
  - VyOS
- Configurable support for any other [supported platform](https://hyperglass.dev/platforms)
- Optionally access devices via an SSH proxy/jump server
- Access-list/prefix-list style query control to whitelist or blacklist query targets
- REST API with automatic, configurable OpenAPI documentation
- Modern, responsive UI built on [ReactJS](https://reactjs.org/), with [NextJS](https://nextjs.org/) & [Chakra UI](https://chakra-ui.com/), written in [TypeScript](https://www.typescriptlang.org/)
- Query multiple devices simultaneously
- Browser-based DNS-over-HTTPS resolution of FQDN queries

*To request support for a specific platform, please [submit a Github Issue](https://github.com/thatmattlove/hyperglass/issues/new) with the **feature** label.*

### [Get Started →](https://hyperglass.dev/installation)

## Community

- [Slack](https://netdev.chat/)
- [Telegram](https://t.me/hyperglasslg)

Any users, potential users, or contributors of hyperglass are welcome to join and discuss usage, feature requests, bugs, and other things.

**hyperglass is developed with the express intention of being free to the networking community**.

*However, if you're feeling particularly helpful or generous, small donations are welcome.*

[![Donate](https://img.shields.io/badge/Donate-blue.svg?logo=paypal&style=for-the-badge)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ZQFH3BB2B5M3E&source=url)

## Acknowledgements

hyperglass is built entirely on open-source software. Here are some of the awesome libraries used, check them out too!

- [Netmiko](https://github.com/ktbyers/netmiko)
- [Litestar](https://litestar.dev)
- [Pydantic](https://docs.pydantic.dev/latest/)
- [Chakra UI](https://chakra-ui.com/)

[![GitHub](https://img.shields.io/github/license/thatmattlove/hyperglass?color=330036&style=for-the-badge)](https://github.com/thatmattlove/hyperglass/blob/main/LICENSE)
