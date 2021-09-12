"""Scrapli-Specific Classes & Utilities.

https://github.com/carlmontanari/scrapli
"""

# Standard Library
import math
from typing import Tuple

# Third Party
from scrapli.driver import AsyncGenericDriver
from scrapli.exceptions import (
    ScrapliTimeout,
    ScrapliException,
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
from hyperglass.configuration import params
from hyperglass.exceptions.public import (
    AuthError,
    ScrapeError,
    DeviceTimeout,
    ResponseEmpty,
)
from hyperglass.exceptions.private import UnsupportedDevice

# Local
from .ssh import SSHConnection

SCRAPLI_DRIVER_MAP = {
    "arista_eos": AsyncEOSDriver,
    "bird": AsyncGenericDriver,
    "cisco_ios": AsyncIOSXEDriver,
    "cisco_nxos": AsyncNXOSDriver,
    "cisco_xr": AsyncIOSXRDriver,
    "frr": AsyncGenericDriver,
    "juniper": AsyncJunosDriver,
    "tnsr": AsyncGenericDriver,
}

driver_global_args = {
    # Per-NOS driver keyword arguments
    "tnsr": {"comms_prompt_pattern": r"\S+\s\S+[\#\>]"},
    "frr": {"comms_ansi": True},
    "bird": {"comms_ansi": True},
}


def _map_driver(nos: str) -> AsyncGenericDriver:
    driver = SCRAPLI_DRIVER_MAP.get(nos)
    if driver is None:
        raise UnsupportedDevice("{nos} is not supported by scrapli.", nos=nos)
    return driver


class ScrapliConnection(SSHConnection):
    """Handle a device connection via Scrapli."""

    async def collect(self, host: str = None, port: int = None) -> Tuple[str, ...]:
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

        global_args = driver_global_args.get(self.device.nos, {})

        driver_kwargs = {
            "host": host or self.device._target,
            "port": port or self.device.port,
            "auth_username": self.device.credential.username,
            "timeout_ops": math.floor(params.request_timeout * 1.25),
            "transport": "asyncssh",
            "auth_strict_key": False,
            "ssh_known_hosts_file": False,
            **global_args,
        }

        if self.device.credential._method == "password":
            # Use password auth if no key is defined.
            driver_kwargs["auth_password"] = self.device.credential.password.get_secret_value()
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
        driver.logger = log.bind(logger_name=f"scrapli.{driver.host}:{driver.port}-driver")
        try:
            responses = ()
            async with driver as connection:
                await connection.get_prompt()
                for query in self.query:
                    raw = await connection.send_command(query)
                    responses += (raw.result,)
                    log.debug(f'Raw response for command "{query}":\n{raw.result}')

        except ScrapliTimeout as err:
            raise DeviceTimeout(error=err, device=self.device)

        except ScrapliAuthenticationFailed as err:
            raise AuthError(error=err, device=self.device)

        except ScrapliException as err:
            raise ScrapeError(error=err, device=self.device)

        if not responses:
            raise ResponseEmpty(query=self.query_data)

        return responses
