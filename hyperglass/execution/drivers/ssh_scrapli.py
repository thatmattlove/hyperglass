"""Scrapli-Specific Classes & Utilities.

https://github.com/carlmontanari/scrapli
"""

# Standard Library
import math
from typing import Iterable

# Third Party
from scrapli.driver import AsyncGenericDriver
from scrapli.exceptions import (
    ScrapliTimeout,
    ScrapliException,
    KeyVerificationFailed,
    ScrapliAuthenticationFailed,
)
from scrapli.driver.core import (
    AsyncEOSDriver,
    AsyncNXOSDriver,
    AsyncIOSXEDriver,
    AsyncIOSXRDriver,
    AsyncJunosDriver,
)

# Project
from hyperglass.log import log
from hyperglass.exceptions import (
    AuthError,
    ScrapeError,
    DeviceTimeout,
    UnsupportedDevice,
)
from hyperglass.configuration import params

# Local
from .ssh import SSHConnection

SCRAPLI_DRIVER_MAP = {
    "cisco_ios": AsyncIOSXEDriver,
    "cisco_nxos": AsyncNXOSDriver,
    "cisco_xr": AsyncIOSXRDriver,
    "juniper": AsyncJunosDriver,
    "arista_eos": AsyncEOSDriver,
}


def _map_driver(nos: str) -> AsyncGenericDriver:
    driver = SCRAPLI_DRIVER_MAP.get(nos)
    if driver is None:
        raise UnsupportedDevice("{nos} is not supported by scrapli.", nos=nos)
    return driver


class ScrapliConnection(SSHConnection):
    """Handle a device connection via Scrapli."""

    async def collect(self, host: str = None, port: int = None) -> Iterable:
        """Connect directly to a device.

        Directly connects to the router via Netmiko library, returns the
        command output.
        """
        driver = _map_driver(self.device.nos)

        if host is not None:
            log.debug(
                "Connecting to {} via proxy {} [{}]",
                self.device.name,
                self.device.proxy.name,
                f"{host}:{port}",
            )
        else:
            log.debug("Connecting directly to {}", self.device.name)

        driver_kwargs = {
            "host": host or self.device._target,
            "port": port or self.device.port,
            "auth_username": self.device.credential.username,
            "timeout_transport": math.floor(params.request_timeout * 1.25),
            "transport": "asyncssh",
            "auth_strict_key": False,
            "ssh_known_hosts_file": False,
            "ssh_config_file": False,
        }

        if self.device.credential._method == "password":
            # Use password auth if no key is defined.
            driver_kwargs[
                "auth_password"
            ] = self.device.credential.password.get_secret_value()
        else:
            # Otherwise, use key auth.
            driver_kwargs["auth_private_key"] = self.device.credential.key.as_posix()
            if self.device.credential._method == "encrypted_key":
                # If the key is encrypted, use the password field as the
                # private key password.
                driver_kwargs[
                    "auth_private_key_passphrase"
                ] = self.device.credential.password.get_secret_value()

        driver = driver(**driver_kwargs)
        driver.logger = log.bind(logger_name=f"scrapli.driver-{driver._host}")

        try:
            responses = ()

            async with driver as connection:
                await connection.get_prompt()
                for query in self.query:
                    raw = await connection.send_command(query)
                    responses += (raw.result,)
                    log.debug(f'Raw response for command "{query}":\n{raw.result}')

        except ScrapliTimeout as err:
            log.error(err)
            raise DeviceTimeout(
                params.messages.connection_error,
                device_name=self.device.display_name,
                proxy=None,
                error=params.messages.request_timeout,
            )
        except (ScrapliAuthenticationFailed, KeyVerificationFailed) as err:
            log.error(
                "Error authenticating to device {loc}: {e}",
                loc=self.device.name,
                e=str(err),
            )

            raise AuthError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                proxy=None,
                error=params.messages.authentication_error,
            )
        except ScrapliException as err:
            log.error(err)
            raise ScrapeError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                proxy=None,
                error=params.messages.no_response,
            )

        if not responses:
            raise ScrapeError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                proxy=None,
                error=params.messages.no_response,
            )

        return responses
