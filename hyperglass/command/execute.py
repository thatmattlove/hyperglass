"""
Accepts input from front end application, validates the input and
returns errors if input is invalid. Passes validated parameters to
construct.py, which is used to build & run the Netmiko connectoins or
hyperglass-frr API calls, returns the output back to the front end.
"""

import re

# Third Party Imports
import httpx
import sshtunnel
from logzero import logger as log
from netmiko import ConnectHandler
from netmiko import NetMikoAuthenticationException
from netmiko import NetmikoAuthError
from netmiko import NetmikoTimeoutError
from netmiko import NetMikoTimeoutException

# Project Imports
from hyperglass.command.construct import Construct
from hyperglass.command.validate import Validate
from hyperglass.configuration import credentials
from hyperglass.configuration import devices
from hyperglass.configuration import logzero_config  # noqa: F401
from hyperglass.configuration import stack  # NOQA: F401
from hyperglass.configuration import params
from hyperglass.configuration import proxies
from hyperglass.constants import Supported
from hyperglass.constants import protocol_map
from hyperglass.exceptions import AuthError, RestError, ScrapeError, DeviceTimeout


class Connect:
    """
    Parent class for all connection types:

    scrape_direct() directly connects to devices via SSH

    scrape_proxied() connects to devices via an SSH proxy

    rest() connects to devices via HTTP for RESTful API communication
    """

    def __init__(self, device_config, query_data, transport):
        self.device_config = device_config
        self.query_data = query_data
        self.query_type = self.query_data["query_type"]
        self.query_target = self.query_data["query_target"]
        self.transport = transport
        self.cred = getattr(credentials, device_config.credential)
        self.query = getattr(
            Construct(
                device=self.device_config,
                query_data=self.query_data,
                transport=self.transport,
            ),
            self.query_type,
        )()

    async def scrape_proxied(self):
        """
        Connects to the router via Netmiko library via the sshtunnel
        library, returns the command output.
        """
        device_proxy = getattr(proxies, self.device_config.proxy)

        log.debug(f"Connecting to {self.device_config.proxy} via sshtunnel library...")
        try:
            tunnel = sshtunnel.open_tunnel(
                device_proxy.address.compressed,
                device_proxy.port,
                ssh_username=device_proxy.username,
                ssh_password=device_proxy.password.get_secret_value(),
                remote_bind_address=(
                    self.device_config.address.compressed,
                    self.device_config.port,
                ),
                local_bind_address=("localhost", 0),
                skip_tunnel_checkup=False,
                logger=log,
            )
        except sshtunnel.BaseSSHTunnelForwarderError as scrape_proxy_error:
            log.error(
                f"Error connecting to device {self.device_config.location} via "
                f"proxy {self.device_config.proxy}"
            )
            raise ScrapeError(
                params.messages.connection_error,
                device_name=self.device_config.display_name,
                proxy=self.device_config.proxy,
                error=scrape_proxy_error,
            )
        with tunnel:
            log.debug(f"Established tunnel with {self.device_config.proxy}")
            scrape_host = {
                "host": "localhost",
                "port": tunnel.local_bind_port,
                "device_type": self.device_config.nos,
                "username": self.cred.username,
                "password": self.cred.password.get_secret_value(),
                "global_delay_factor": 0.2,
                "timeout": params.general.request_timeout - 1,
            }
            log.debug(f"SSH proxy local binding: localhost:{tunnel.local_bind_port}")
            try:
                log.debug(
                    f"Connecting to {self.device_config.location} "
                    "via Netmiko library..."
                )
                nm_connect_direct = ConnectHandler(**scrape_host)
                responses = []
                for query in self.query:
                    raw = nm_connect_direct.send_command(query)
                    responses.append(raw)
                    log.debug(f'Raw response for command "{query}":\n{raw}')
                response = "\n\n".join(responses)
                log.debug(f"Response type:\n{type(response)}")

            except (NetMikoTimeoutException, NetmikoTimeoutError) as scrape_error:
                log.error(
                    f"Timeout connecting to device {self.device_config.location}: "
                    f"{scrape_error}"
                )
                raise DeviceTimeout(
                    params.messages.connection_error,
                    device_name=self.device_config.display_name,
                    proxy=self.device_config.proxy,
                    error=params.messages.request_timeout,
                )
            except (NetMikoAuthenticationException, NetmikoAuthError) as auth_error:
                log.error(
                    f"Error authenticating to device {self.device_config.location}: "
                    f"{auth_error}"
                )
                raise AuthError(
                    params.messages.connection_error,
                    device_name=self.device_config.display_name,
                    proxy=self.device_config.proxy,
                    error=params.messages.authentication_error,
                ) from None
            except sshtunnel.BaseSSHTunnelForwarderError as scrape_error:
                log.error(
                    f"Error connecting to device proxy {self.device_config.proxy}: "
                    f"{scrape_error}"
                )
                raise ScrapeError(
                    params.messages.connection_error,
                    device_name=self.device_config.display_name,
                    proxy=self.device_config.proxy,
                    error=params.messages.general,
                )
        if response is None:
            log.error(f"No response from device {self.device_config.location}")
            raise ScrapeError(
                params.messages.connection_error,
                device_name=self.device_config.display_name,
                proxy=None,
                error=params.messages.noresponse_error,
            )
        log.debug(f"Output for query: {self.query}:\n{response}")
        return response

    async def scrape_direct(self):
        """
        Directly connects to the router via Netmiko library, returns the
        command output.
        """

        log.debug(f"Connecting directly to {self.device_config.location}...")

        scrape_host = {
            "host": self.device_config.address.compressed,
            "port": self.device_config.port,
            "device_type": self.device_config.nos,
            "username": self.cred.username,
            "password": self.cred.password.get_secret_value(),
            "global_delay_factor": 0.2,
            "timeout": params.general.request_timeout - 1,
        }

        try:
            log.debug(f"Device Parameters: {scrape_host}")
            log.debug(
                f"Connecting to {self.device_config.location} via Netmiko library"
            )
            nm_connect_direct = ConnectHandler(**scrape_host)
            responses = []
            for query in self.query:
                raw = nm_connect_direct.send_command(query)
                responses.append(raw)
                log.debug(f'Raw response for command "{query}":\n{raw}')
            response = "\n\n".join(responses)
            log.debug(f"Response type:\n{type(response)}")
        except (NetMikoTimeoutException, NetmikoTimeoutError) as scrape_error:
            log.error(f"{params.general.request_timeout - 1} second timeout expired.")
            log.error(scrape_error)
            raise DeviceTimeout(
                params.messages.connection_error,
                device_name=self.device_config.display_name,
                proxy=None,
                error=params.messages.request_timeout,
            )
        except (NetMikoAuthenticationException, NetmikoAuthError) as auth_error:
            log.error(f"Error authenticating to device {self.device_config.location}")
            log.error(auth_error)

            raise AuthError(
                params.messages.connection_error,
                device_name=self.device_config.display_name,
                proxy=None,
                error=params.messages.authentication_error,
            )
        if response is None:
            log.error(f"No response from device {self.device_config.location}")
            raise ScrapeError(
                params.messages.connection_error,
                device_name=self.device_config.display_name,
                proxy=None,
                error=params.messages.noresponse_error,
            )
        log.debug(f"Output for query: {self.query}:\n{response}")
        return response

    async def rest(self):
        """Sends HTTP POST to router running a hyperglass API agent"""
        log.debug(f"Query parameters: {self.query}")

        uri = Supported.map_rest(self.device_config.nos)
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.cred.password.get_secret_value(),
        }
        http_protocol = protocol_map.get(self.device_config.port, "http")
        endpoint = "{protocol}://{addr}:{port}/{uri}".format(
            protocol=http_protocol,
            addr=self.device_config.address.exploded,
            port=self.device_config.port,
            uri=uri,
        )

        log.debug(f"HTTP Headers: {headers}")
        log.debug(f"URL endpoint: {endpoint}")

        try:
            http_client = httpx.AsyncClient()
            raw_response = await http_client.post(
                endpoint, headers=headers, json=self.query, timeout=7
            )
            response = raw_response.text

            log.debug(f"HTTP status code: {raw_response.status_code}")
            log.debug(f"Output for query {self.query}:\n{response}")
        except (
            httpx.exceptions.ConnectTimeout,
            httpx.exceptions.CookieConflict,
            httpx.exceptions.DecodingError,
            httpx.exceptions.InvalidURL,
            httpx.exceptions.PoolTimeout,
            httpx.exceptions.ProtocolError,
            httpx.exceptions.ReadTimeout,
            httpx.exceptions.RedirectBodyUnavailable,
            httpx.exceptions.RedirectLoop,
            httpx.exceptions.ResponseClosed,
            httpx.exceptions.ResponseNotRead,
            httpx.exceptions.StreamConsumed,
            httpx.exceptions.Timeout,
            httpx.exceptions.TooManyRedirects,
            httpx.exceptions.WriteTimeout,
        ) as rest_error:
            rest_msg = " ".join(
                re.findall(r"[A-Z][^A-Z]*", rest_error.__class__.__name__)
            )
            log.error(
                f"Error connecting to device {self.device_config.location}: {rest_msg}"
            )
            raise RestError(
                params.messages.connection_error,
                device_name=self.device_config.display_name,
                error=rest_msg,
            )
        except OSError:
            raise RestError(
                params.messages.connection_error,
                device_name=self.device_config.display_name,
                error="System error",
            )

        if raw_response.status_code != 200:
            log.error(f"Response code is {raw_response.status_code}")
            raise RestError(
                params.messages.connection_error,
                device_name=self.device_config.display_name,
                error=params.messages.general,
            )

        if not response:
            log.error(f"No response from device {self.device_config.location}")
            raise RestError(
                params.messages.connection_error,
                device_name=self.device_config.display_name,
                error=params.messages.noresponse_error,
            )

        log.debug(f"Output for query: {self.query}:\n{response}")
        return response


class Execute:
    """
    Ingests raw user input, performs validation of target input, pulls
    all configuraiton variables for the input router and connects to the
    selected device to execute the query.
    """

    def __init__(self, lg_data):
        self.query_data = lg_data
        self.query_location = self.query_data["query_location"]
        self.query_type = self.query_data["query_type"]
        self.query_target = self.query_data["query_target"]

    async def response(self):
        """
        Initializes Execute.filter(), if input fails to pass filter,
        returns errors to front end. Otherwise, executes queries.
        """
        device_config = getattr(devices, self.query_location)

        log.debug(f"Received query for {self.query_data}")
        log.debug(f"Matched device config: {device_config}")

        # Run query parameters through validity checks
        validation = Validate(device_config, self.query_data, self.query_target)
        valid_input = validation.validate_query()
        if valid_input:
            log.debug(f"Validation passed for query: {self.query_data}")
            pass

        connect = None
        output = params.messages.general

        transport = Supported.map_transport(device_config.nos)
        connect = Connect(device_config, self.query_data, transport)

        if Supported.is_rest(device_config.nos):
            output = await connect.rest()
        elif Supported.is_scrape(device_config.nos):
            if device_config.proxy:
                output = await connect.scrape_proxied()
            else:
                output = await connect.scrape_direct()
        return output
