"""Execute validated & constructed query on device.

Accepts input from front end application, validates the input and
returns errors if input is invalid. Passes validated parameters to
construct.py, which is used to build & run the Netmiko connections or
hyperglass-frr API calls, returns the output back to the front end.
"""

# Standard Library
import math
from typing import Callable, Iterable

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
from hyperglass.compat._sshtunnel import BaseSSHTunnelForwarderError, open_tunnel
from hyperglass.execution.drivers._common import Connection


class SSHConnection(Connection):
    """Connect to target device via specified transport.

    scrape_direct() directly connects to devices via SSH

    scrape_proxied() connects to devices via an SSH proxy

    rest() connects to devices via HTTP for RESTful API communication
    """

    def setup_proxy(self) -> Callable:
        """Return a preconfigured sshtunnel.SSHTunnelForwarder instance."""

        proxy = self.device.proxy

        def opener():
            """Set up an SSH tunnel according to a device's configuration."""
            try:
                return open_tunnel(
                    proxy.address,
                    proxy.port,
                    ssh_username=proxy.credential.username,
                    ssh_password=proxy.credential.password.get_secret_value(),
                    remote_bind_address=(self.device.address, self.device.port),
                    local_bind_address=("localhost", 0),
                    skip_tunnel_checkup=False,
                    gateway_timeout=params.request_timeout - 2,
                )

            except BaseSSHTunnelForwarderError as scrape_proxy_error:
                log.error(
                    f"Error connecting to device {self.device.name} via "
                    f"proxy {proxy.name}"
                )
                raise ScrapeError(
                    params.messages.connection_error,
                    device_name=self.device.display_name,
                    proxy=proxy.name,
                    error=str(scrape_proxy_error),
                )

        return opener

    async def netmiko(self, host: str = None, port: int = None) -> Iterable:
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
