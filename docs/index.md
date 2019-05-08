<img src="/hyperglass-dark.png" width=300></img>

# What is Hyperglass?

**Hyperglass** is an open source looking glass application to provide customers, peers, and partners of network operators with unattended visibility into the operator's network.

# Yet Another Looking Glass?

Many of the more popular open source looking glass applications are written in PHP or Perl, languages infrequently used by many network engineers today. With the widespread adoption of network operations tooling such as [Netmiko](https://github.com/ktbyers/netmiko), [Netbox](https://github.com/digitalocean/netbox), and [Napalm](https://github.com/napalm-automation/napalm), Python is most often the language of choice for network operators. Hyperglass is built completely on Python 3 and utilizes user-friendly configuration files to provide a highly customizable, easy to deploy looking glass app.

Hyperglass was created with the lofty goal of benefiting the internet community at-large, by providing an easier and more familiar way for operators to provide looking glass services to their customers, peers, and partners.

# Application Stack

| Function                   | Component |
| -------------------------- | --------- |
| Front End Framework        | Bulma     |
| Front End Application      | Flask     |
| Back End Application       | Python 3  |
| Device Connection Handling | Netmiko   |
| Configuration Format       | TOML      |

# Get Started

See the [installation guide](<>) to get started.
