Proxy servers are defined in `hyperglass/hyperglass/configuration/devices.toml`. Each proxy definition is a unique TOML table, for example:

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

When a proxy server is defined under the `[[router]]` heading in `devices.toml`, the defined proxy name is matched to a configured proxy as shown above. When the connection to the device is initiated, the hyperglass server will first initiate an SSH connection to the proxy, and then initiate a second connection to the target device (router) *from* the proxy server. This can be helpful if you want to secure access to your routers.

#### address

IP address hyperglass will use to connect to the device.

#### username

Username for SSH authentication to the proxy server/jumpbox. SSH Key authentication is not yet supported.

#### password

Plain text password for SSH authentication to the proxy server/jumpbox.

!!! warning "Security Warning"
    These values are stored in plain text. Make sure the accounts are restricted and that the configuration file is stored in a secure location.

#### type

Device type/vendor name as recognized by [Netmiko](https://github.com/ktbyers/netmiko). See [supported device types](#supported-device-types) for a full list.

!!! note "Compatibility"
    Hyperglass has only been tested with `linux_ssh` as of this writing.

#### ssh_command

Command used to initiate an SSH connection *from* the proxy server to the target device. `{username}` will map to the target device (router) username as defined in its associated credential mapping. `{host}` will map to the target device IP address as defined in `devices.toml`.
