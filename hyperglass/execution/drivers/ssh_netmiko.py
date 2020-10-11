"""Netmiko-Specific Classes & Utilities.

https://github.com/ktbyers/netmiko
"""

# Standard Library
import math
from typing import Iterable

# Third Party
from netmiko import (
    ConnectHandler,
    NetMikoTimeoutException,
    NetMikoAuthenticationException,
)

# Project
from hyperglass.log import log
from hyperglass.exceptions import AuthError, ScrapeError, DeviceTimeout
from hyperglass.configuration import params

# Local
from .ssh import SSHConnection

netmiko_nos_globals = {
    # Netmiko doesn't currently handle Mikrotik echo verification well,
    # see ktbyers/netmiko#1600
    "mikrotik_routeros": {"global_cmd_verify": False},
    "mikrotik_switchos": {"global_cmd_verify": False},
}

netmiko_nos_send_args = {
    # Netmiko doesn't currently handle the Mikrotik prompt properly, see
    # ktbyers/netmiko#1956
    "mikrotik_routeros": {"expect_string": r"\S+\s\>\s$"},
    "mikrotik_switchos": {"expect_string": r"\S+\s\>\s$"},
}


class NetmikoConnection(SSHConnection):
    """Handle a device connection via Netmiko."""

    async def collect(self, host: str = None, port: int = None) -> Iterable:
        """Connect directly to a device.

        Directly connects to the router via Netmiko library, returns the
        command output.
        """
        if host is not None:
            log.debug(
                "Connecting to {} via proxy {} [{}]",
                self.device.name,
                self.device.proxy.name,
                f"{host}:{port}",
            )
        else:
            log.debug("Connecting directly to {}", self.device.name)

        global_args = netmiko_nos_globals.get(self.device.nos, {})

        send_args = netmiko_nos_send_args.get(self.device.nos, {})

        driver_kwargs = {
            "host": host or self.device._target,
            "port": port or self.device.port,
            "device_type": self.device.nos,
            "username": self.device.credential.username,
            "global_delay_factor": params.netmiko_delay_factor,
            "timeout": math.floor(params.request_timeout * 1.25),
            "session_timeout": math.ceil(params.request_timeout - 1),
            **global_args,
        }

        if self.device.credential._method == "password":
            # Use password auth if no key is defined.
            driver_kwargs[
                "password"
            ] = self.device.credential.password.get_secret_value()
        else:
            # Otherwise, use key auth.
            driver_kwargs["use_keys"] = True
            driver_kwargs["key_file"] = self.device.credential.key
            if self.device.credential._method == "encrypted_key":
                # If the key is encrypted, use the password field as the
                # private key password.
                driver_kwargs[
                    "passphrase"
                ] = self.device.credential.password.get_secret_value()

        try:
            nm_connect_direct = ConnectHandler(**driver_kwargs)

            responses = ()

            for query in self.query:
                raw = nm_connect_direct.send_command(query, **send_args)
                responses += (raw,)
                log.debug(f'Raw response for command "{query}":\n{raw}')

            nm_connect_direct.disconnect()

        except NetMikoTimeoutException as scrape_error:
            log.error(str(scrape_error))
            raise DeviceTimeout(
                params.messages.connection_error,
                device_name=self.device.display_name,
                proxy=None,
                error=params.messages.request_timeout,
            )
        except NetMikoAuthenticationException as auth_error:
            log.error(
                "Error authenticating to device {loc}: {e}",
                loc=self.device.name,
                e=str(auth_error),
            )

            raise AuthError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                proxy=None,
                error=params.messages.authentication_error,
            )
        if not responses:
            raise ScrapeError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                proxy=None,
                error=params.messages.no_response,
            )

        return responses
