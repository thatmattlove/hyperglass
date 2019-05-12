Authentication parameters are stored in the `devices.toml` file, at `hyperglass/hyperglass/configuration/devices.toml`. The array of tables simply stores the username and password for a device. SSH Key authentication is not yet supported.

Example:

```toml
[credential.'default']
username = "hyperglass"
password = "secret_password"

[credential.'other_credential']
username = "other_username"
password = "other_secret_password"
```

!!! warning "Security Warning"
    These values are stored in plain text. Make sure the accounts are restricted and that the configuration file is stored in a secure location.
