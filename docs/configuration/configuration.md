# Configuration

Hyperglass configuration files are stored in `hyperglass/hyperglass/configuration/`, in [TOML](https://github.com/toml-lang/toml) format.

```console
hyperglass/configuration/
├── commands.toml
├── configuration.toml
└── devices.toml
```

## Site Parameters

Global hyperglass parameters

#### debug

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `false`       |

Enables hyperglass & Flask debugging.

!!! warning "Logging"
    Enabling debug mode will produce a large amount of log output, as every configuration parameter and backend transaction is logged to stdout.

#### requires_ipv6_cidr

| Type  | Default Value                 |
| ----- | ----------------------------- |
| Array | `["cisco_ios", "cisco_nxos"]` |

Some platforms (namely Cisco IOS) are unable to perform a BGP lookup by IPv6 host address (e.g. 2001:db8::1), but must perform the lookup by prefix (e.g. 2001:db8::/48). `requires_ipv6_cidr` is a list (TOML array) of network operating systems that require this (in Netmiko format).

If a user attempts to query a device requiring IPv6 lookups in CIDR format with an IPv6 host address, the following message will be displayed:

<img src="/requires_ipv6_cidr.png" style="width: 70%"></img>

#### blacklist

| Type  | Default Value |
| ----- | ------------- |
| Array | See Example   |

The blacklist is a simple TOML array (list) of host IPs or prefixes that you do not want end users to be able to query. For example, if you have one or more hosts/subnets you wish to prevent users from looking up (or any contained host or prefix), add them to the list.

##### Example

```toml
blacklist = [
"198.18.0.0/15",
"2001:db8::/32",
"10.0.0.0/8",
"192.168.0.0/16",
"172.16.0.0/12"
]
```

When users attempt to query a matching host/prefix, they will receive the following error message by default:

<img src="/blacklist_error.png" style="width: 70%"></img>

## `[general]` - Site Parameters

#### primary_asn

| Type   | Default Value |
| ------ | ------------- |
| String | `"65000"`     |

Your network's _primary_ ASN. Number only, e.g. `65000`, **not** `AS65000`.

#### google_analytics

| Type   | Default Value |
| ------ | ------------- |
| String | `""`          |

Google Analytics ID number. For more information on how to set up Google Analytics, see [here](https://support.google.com/analytics/answer/1008080?hl=en).
