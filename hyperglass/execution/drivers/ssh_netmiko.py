"""Netmiko-Specific Classes & Utilities.

https://github.com/ktbyers/netmiko
"""

# Standard Library
import math
from typing import Iterable

# Third Party
from netmiko import (
    ConnectHandler,
    NetmikoAuthError,
    NetmikoTimeoutError,
    NetMikoTimeoutException,
    NetMikoAuthenticationException,
)

# Project
from hyperglass.log import log
from hyperglass.exceptions import AuthError, ScrapeError, DeviceTimeout
from hyperglass.configuration import params
from hyperglass.execution.drivers.ssh import SSHConnection


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

        netmiko_args = {
            "host": host or self.device.address,
            "port": port or self.device.port,
            "device_type": self.device.nos,
            "username": self.device.credential.username,
            "password": self.device.credential.password.get_secret_value(),
            "global_delay_factor": params.netmiko_delay_factor,
            "timeout": math.floor(params.request_timeout * 1.25),
            "session_timeout": math.ceil(params.request_timeout - 1),
        }

        try:
            nm_connect_direct = ConnectHandler(**netmiko_args)

            responses = ()

            for query in self.query:
                raw = nm_connect_direct.send_command(query)
                responses += (raw,)
                log.debug(f'Raw response for command "{query}":\n{raw}')

            nm_connect_direct.disconnect()

        except (NetMikoTimeoutException, NetmikoTimeoutError) as scrape_error:
            log.error(str(scrape_error))
            raise DeviceTimeout(
                params.messages.connection_error,
                device_name=self.device.display_name,
                proxy=None,
                error=params.messages.request_timeout,
            )
        except (NetMikoAuthenticationException, NetmikoAuthError) as auth_error:
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
