# Configuration

Hyperglass configuration files are stored `hyperglass/hyperglass/config`, in [TOML](https://github.com/toml-lang/toml) format.

Example configuration files are provided and end in `.example`. All example configuration files should be copied to their `.toml` name & extension. For example:

```console
$ cd hyperglass/hyperglass/config
$
$ cp blacklist.toml.example blacklist.toml
$ cp commands.toml.example commands.toml
$ cp config.toml.example config.toml
$ cp devices.toml.example devices.toml
```

## `requires_ipv6_cidr.toml`

Some platforms (namely Cisco IOS) are unable to perform a BGP lookup by IPv6 host address (e.g. 2001:db8::1), but must perform the lookup by prefix (e.g. 2001:db8::/48). `requires_ipv6_cidr.toml` is a list (TOML array) of network operating systems that require this (in Netmiko format).
