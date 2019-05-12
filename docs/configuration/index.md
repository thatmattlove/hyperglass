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

## `requires_ipv6_cidr.toml`

Some platforms (namely Cisco IOS) are unable to perform a BGP lookup by IPv6 host address (e.g. 2001:db8::1), but must perform the lookup by prefix (e.g. 2001:db8::/48). `requires_ipv6_cidr.toml` is a list (TOML array) of network operating systems that require this (in Netmiko format).
