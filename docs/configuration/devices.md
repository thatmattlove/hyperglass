Devices/routers are defined in `hyperglass/hyperglass/configuration/devices.toml`. `devices.toml` is effectively an array of hash tables/dictionaries/key value pairs:

```toml
[[router]]
address = "10.0.0.1"
asn = "65000"
src_addr_ipv4 = "192.0.2.1"
src_addr_ipv6 = "2001:db8::1"
credential = "default"
location = "pop1"
name = "router1.pop1"
port = "22"
type = "cisco_xr"
proxy = "jumpbox1"

[[router]]
address = "10.0.0.2"
asn = "65000"
src_addr_ipv4 = "192.0.2.2"
src_addr_ipv6 = "2001:db8::2"
credential = "default"
location = "pop2"
name = "router1.pop2"
port = "22"
type = "cisco_ios"
proxy = "jumpbox2"

[[router]]
address = "10.0.0.3"
asn = "65000"
src_addr_ipv4 = "192.0.2.3"
src_addr_ipv6 = "2001:db8::3"
credential = "default"
location = "pop3"
name = "router1.pop3"
port = "22"
type = "juniper"
proxy = "jumpbox3"
```

### Device Keys

#### address

IP address hyperglass will use to connect to the device.

#### asn

ASN this device is a member of.

#### src_addr_ipv4

Source IPv4 address used for `ping` and `traceroute` queries.

#### src_addr_ipv6

Source IPv6 address used for `ping` and `traceroute` queries.

#### credential

Name of credential (username & password) used to authenticate with the device. Credentials are defined as individual tables. See [here](/configuration/authentication.md) for more information on authentication.

#### location

Name of location/POP where this device resides.

#### name

Display name/hostname of device.

#### port

TCP port for SSH connection to device.

#### type

Device type/vendor name as recognized by [Netmiko](https://github.com/ktbyers/netmiko). See [supported device types](#supported-device-types) for a full list.

#### proxy

Name of SSH proxy/jumpbox, if any, used for connecting to the device. See [here](/configuration/proxy.md) for more information on proxying.

### Supported Device Types

Updated **2019-04-28** from [Netmiko](https://github.com/ktbyers/netmiko/blob/master/netmiko/ssh_dispatcher.py#L76).

```console
a10
accedian
alcatel_aos
alcatel_sros
apresia_aeos
arista_eos
aruba_os
avaya_ers
avaya_vsp
brocade_fastiron
brocade_netiron
brocade_nos
brocade_vdx
brocade_vyos
checkpoint_gaia
calix_b6
ciena_saos
cisco_asa
cisco_ios
cisco_nxos
cisco_s300
cisco_tp
cisco_wlc
cisco_xe
cisco_xr
coriant
dell_dnos9
dell_force10
dell_os6
dell_os9
dell_os10
dell_powerconnect
dell_isilon
eltex
enterasys
extreme
extreme_ers
extreme_exos
extreme_netiron
extreme_nos
extreme_slx
extreme_vdx
extreme_vsp
extreme_wing
f5_ltm
f5_tmsh
f5_linux
fortinet
generic_termserver
hp_comware
hp_procurve
huawei
huawei_vrpv8
ipinfusion_ocnos
juniper
juniper_junos
linux
mellanox
mrv_optiswitch
netapp_cdot
netscaler
oneaccess_oneos
ovs_linux
paloalto_panos
pluribus
quanta_mesh
rad_etx
ruckus_fastiron
ubiquiti_edge
ubiquiti_edgeswitch
vyatta_vyos
vyos
```
