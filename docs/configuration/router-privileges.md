More than likely, you'll want to "lock down" what commands can be executed with the credentials you've provided in `hyperglass/hyperglass/config/devices.toml`. It is **strongly** recommended to use a low privilege read only account and not your full administrator account. Even though Hyperglass is coded to only run certain commands to begin with, you're more than likely still exposing the server Hyperglass runs on to the internet, and on that server is a plain text file with your router's credentials in it. Take precautions.

# Creating Restricted Accounts

## Cisco IOS

On Cisco IOS, **parser views** are the recommended tool to restrict access. Basic instructions for configuring Cisco IOS parser views for the default enabled query types are below:

```
parser view hyperglass
 secret <secret>
 commands exec include all terminal width
 commands exec include all terminal length
 commands exec include all traceroute
 commands exec include all ping
 commands exec include all show bgp
!
username hyperglass privilege 15 view hyperglass secret <secret>
```

!!! info "Terminal"
    The `terminal length` and `terminal width` commands are required by Netmiko for session handling. If you remove these, Hyperglass will not work.

## Cisco IOS-XR

On Cisco IOS-XR, **taskgroups** are the recommended tool to restrict access. Basic instructoins for configuring Cisco IOS-XR taskgroups for the default enabled query types are below:

```
taskgroup hyperglass
 task read bgp
!
usergroup hyperglass
 taskgroup hyperglass
!
username hyperglass
 group hyperglass
 group operator
 secret <secret>
```


!!! warning "IOS-XR"
    I have not yet figured out a way to enable all the extended options for `ping` and `traceroute` (source IP, count, etc.) without adding the `group operator` statement to the taskgroup. If anyone knows of a way to do this, I welcome a docs PR.

## Juniper

On JunOS, **system login classes** are the recommended tool to restrict access. Basic instructoins for configuring Juniper JunOS login classes for the default enabled query types are below:

```
edit system login class hyperglass

set permissions floppy

set allow-commands-regexp [ "show route protocol bgp" ping traceroute "show route protocol bgp table inet.0" "show route protocol bgp table inet6.0" "ping inet" "ping inet6" "traceroute inet" "traceroute inet6" ]

top
set system login user hyperglass class hyperglass authentication plain-text-password
```
