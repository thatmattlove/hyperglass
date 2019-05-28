`devices.toml` is structured as three separate hash table/dictionaries for devices, credentials, and proxies. All values are strings.

# Routers

| Parameter         | Function                                                                                                                                                                                                                                                                              |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **address**       | IP address hyperglass will use to connect to the device.                                                                                                                                                                                                                              |
| **asn**           | ASN this device is a member of.                                                                                                                                                                                                                                                       |
| **src_addr_ipv4** | Source IPv4 address used for ping and traceroute queries.                                                                                                                                                                                                                             |
| **src_addr_ipv6** | Source IPv6 address used for ping and traceroute queries.                                                                                                                                                                                                                             |
| **credential**    | Name of credential (username & password) used to authenticate with the device. Credentials are defined as individual tables. See [here](/configuration/authentication.md) for more information on authentication.                                                                     |
| **location**      | Name of location/POP where this device resides.                                                                                                                                                                                                                                       |
| **name**          | Hostname of the individual device.                                                                                                                                                                                                                                                    |
| **display_name**  | Device name that will be shown to the end user on the main hyperglass page.                                                                                                                                                                                                           |
| **port**          | TCP port for SSH/HTTP connection to device.                                                                                                                                                                                                                                           |
| **type**          | Device type/vendor name as recognized by [Netmiko](https://github.com/ktbyers/netmiko). See [supported device types](extras/supported-device-types) for a full list. If using FRRouting and the [hyperglass-frr](https://github.com/checktheroads/hyperglass-frr) API, specify `frr`. |
| **proxy**         | Name of SSH proxy/jumpbox, if any, used for connecting to the device. See [here](/configuration/proxy.md) for more information on proxying. If not using a proxy, specify an empty string, i.e. `""`.                                                                                  |

#### Example

```toml
[router.'pop1']
address = "192.0.2.1"
asn = "65000"
src_addr_ipv4 = "192.0.2.251"
src_addr_ipv6 = "2001:db8::1"
credential = "default"
location = "pop1"
name = "router1.pop1"
display_name = "Washington, DC"
port = "22"
type = "cisco_ios"
proxy = "jumpbox1"

[router.'pop2']
address = "192.0.2.2"
asn = "65000"
src_addr_ipv4 = "192.0.2.252"
src_addr_ipv6 = "2001:db8::2"
credential = "frr_api_pop2"
location = "pop2"
name = "router1.pop2"
display_name = "Portland, OR"
port = "8080"
type = "frr"
proxy = ""
```

# Credentials

The credential table stores the username and password for a device. SSH Key authentication is not yet supported. If using FRRouting and the [hyperglass-frr](https://github.com/checktheroads/hyperglass-frr) API, the username can be any arbitrary value (it is not used), and the password is the PBKDF2 SHA256 *hashed* API key (**not** the API key itself).

#### Example

```toml
[credential.'default']
username = "hyperglass"
password = "secret_password"

[credential.'frr_api_pop2']
username = "doesntmatter"
password = "$pbkdf2-sha256$29000$bI0xJqQUQoixtjZGSAnhvA$FM0oUc.Y3kuvl9ilQmMuULTD1MjzD64Ax9rFNUgAl.c"
```

!!! warning "Security Warning"
    These values are stored in plain text, so make sure the accounts are restricted. Instructions for creating restricted accounts on common platforms can be found [here](extras/securing-router-access).

# Proxies
The proxy table stores the connection parameters for an SSH proxy.

When a proxy server is defined in the `[router]` table, the defined proxy name is matched to a configured proxy as shown above. When the connection to the device is initiated, the hyperglass server will first initiate an SSH connection to the proxy, and then initiate a second connection to the target device (router) *from* the proxy server. This can be helpful if you want to secure access to your routers.

!!! warning "Security Warning"
    These values are stored in plain text, so make sure the accounts are restricted.

| Parameter   | Function                                                                                                                                                                                                                                                                               |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **address**     | IP address hyperglass will use to connect to the device.                                                                                                                                                                                                                               |
| **username**    | Username for SSH authentication to the proxy server/jumpbox. SSH Key authentication is not yet supported.                                                                                                                                                                              |
| **password**    | Plain text password for SSH authentication to the proxy server/jumpbox.                                                                                                                                                                                                                |
| **type**        | Device type/vendor name as recognized by [Netmiko](https://github.com/ktbyers/netmiko). See [supported device types](extras/supported-device-types) for a full list.                                                                                                                   |
| **ssh_command** | Command used to initiate an SSH connection _from_ the proxy server to the target device. `{username}` will map to the target device (router) username as defined in its associated credential mapping. `{host}` will map to the target device IP address as defined in `devices.toml`. |

#### Example

```toml
[proxy.'jumpbox1']
address = "10.1.1.1"
username = "hyperglass"
password = "secret_password"
type = "linux_ssh"
ssh_command = "ssh -l {username} {host}"

[proxy.'jumpbox2']
address = "10.1.1.2"
username = "hyperglass"
password = "secret_password"
type = "linux_ssh"
ssh_command = "ssh -l {username} {host}"
```

!!! note "Compatibility"
    Hyperglass has only been tested with `linux_ssh` as of this writing.
