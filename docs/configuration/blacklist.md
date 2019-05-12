Blacklisted querys are defined in `hyperglass/hyperglass/configuration/blacklist.toml`.

The blacklist is a simple TOML array (list) of host IPs or prefixes that you do not want end users to be able to query. For example, if you want to prevent users from looking up 198.18.0.0/15 or any contained host or prefix, you can add it to the blacklist:

```toml
blacklist = [
198.18.0.0/15
]
```

If you have multiple hosts/subnets you wish to blacklist, you can do so by adding a comma `,` after each entry (except the last):

```toml
blacklist = [
'198.18.0.0/15',
'10.0.0.0/8',
'192.168.0.0/16',
'2001:db8::/32'
'172.16.0.0/12'
]
```

When users attempt to query a matching host/prefix, they will receive the following error message by default:

<img src="/blacklist_error.png"></img>
