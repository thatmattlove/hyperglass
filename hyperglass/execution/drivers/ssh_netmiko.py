"""Netmiko-Specific Classes & Utilities.

https://github.com/ktbyers/netmiko
"""

# Standard Library
import math
from typing import Iterable

# Third Party
from netmiko import (  # type: ignore
    ConnectHandler,
    NetMikoTimeoutException,
    NetMikoAuthenticationException,
)

# Project
from hyperglass.log import log
from hyperglass.state import use_state
from hyperglass.exceptions.public import AuthError, DeviceTimeout, ResponseEmpty

# Local
from .ssh import SSHConnection

netmiko_device_globals = {
    # Netmiko doesn't currently handle Mikrotik echo verification well,
    # see ktbyers/netmiko#1600
    "mikrotik_routeros": {"global_cmd_verify": False},
    "mikrotik_switchos": {"global_cmd_verify": False},
}

netmiko_device_send_args = {}


class NetmikoConnection(SSHConnection):
    """Handle a device connection via Netmiko."""

    async def collect(self, host: str = None, port: int = None) -> Iterable:
        """Connect directly to a device.

        Directly connects to the router via Netmiko library, returns the
        command output.
        """
        params = use_state("params")
        _log = log.bind(
            device=self.device.name,
            address=f"{host}:{port}",
            proxy=str(self.device.proxy.address) if self.device.proxy is not None else None,
        )

        _log.debug("Connecting to device")

        global_args = netmiko_device_globals.get(self.device.platform, {})

        send_args = netmiko_device_send_args.get(self.device.platform, {})

        driver_kwargs = {
            "host": host or self.device._target,
            "port": port or self.device.port,
            "device_type": self.device.get_device_type(),
            "username": self.device.credential.username,
            "global_delay_factor": 0.1,
            "timeout": math.floor(params.request_timeout * 1.25),
            "session_timeout": math.ceil(params.request_timeout - 1),
            **global_args,
            **self.device.driver_config,
        }

        if "_telnet" in self.device.platform:
            # Telnet devices with a low delay factor (default) tend to
            # throw login errors.
            driver_kwargs["global_delay_factor"] = 2

        if self.device.credential._method == "password":
            # Use password auth if no key is defined.
            driver_kwargs["password"] = self.device.credential.password.get_secret_value()
        else:
            # Otherwise, use key auth.
            driver_kwargs["use_keys"] = True
            driver_kwargs["key_file"] = self.device.credential.key
            if self.device.credential._method == "encrypted_key":
                # If the key is encrypted, use the password field as the
                # private key password.
                driver_kwargs["passphrase"] = self.device.credential.password.get_secret_value()

        try:
            nm_connect_direct = ConnectHandler(**driver_kwargs)

            responses = ()

            for query in self.query:
                raw = nm_connect_direct.send_command(query, **send_args)
                responses += (raw,)

            nm_connect_direct.disconnect()

        except NetMikoTimeoutException as scrape_error:
            raise DeviceTimeout(error=scrape_error, device=self.device) from scrape_error

        except NetMikoAuthenticationException as auth_error:
            raise AuthError(error=auth_error, device=self.device) from auth_error

        if not responses:
            raise ResponseEmpty(query=self.query_data)

        return responses
