"""
Accepts input from front end application, validates the input and
returns errors if input is invalid. Passes validated parameters to
construct.py, which is used to build & run the Netmiko connectoins or
hyperglass-frr API calls, returns the output back to the front end.
"""

# Third Party Imports
import httpx
import sshtunnel
from logzero import logger
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
from hyperglass.configuration import params
from hyperglass.configuration import proxies
from hyperglass.constants import Supported
from hyperglass.constants import protocol_map
from hyperglass.exceptions import AuthError, RestError, ScrapeError


class Connect:
    """
    Parent class for all connection types:

    scrape() connects to devices via SSH for "screen scraping"

    rest() connects to devices via HTTP for RESTful API communication
    """

    def __init__(self, device_config, query_type, target, transport):
        self.device_config = device_config
        self.query_type = query_type
        self.target = target
        self.transport = transport
        self.cred = getattr(credentials, device_config.credential)
        self.query = getattr(Construct(device_config, transport), query_type)(target)

    async def scrape(self):
        """
        Connects to the router via Netmiko library, return the command
        output. If an SSH proxy is enabled, creates an SSH tunnel via
        the sshtunnel library, and netmiko uses the local binding to
        connect to the remote device.
        """
        response = None
        if self.device_config.proxy:
            device_proxy = getattr(proxies, self.device_config.proxy)
            logger.debug(
                f"Proxy: {device_proxy.address.compressed}:{device_proxy.port}"
            )
            logger.debug(
                "Connecting to {dev} via sshtunnel library...".format(
                    dev=self.device_config.proxy
                )
            )
            with sshtunnel.open_tunnel(
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
            ) as tunnel:
                logger.debug(f"Established tunnel with {self.device_config.proxy}")
                scrape_host = {
                    "host": "localhost",
                    "port": tunnel.local_bind_port,
                    "device_type": self.device_config.nos,
                    "username": self.cred.username,
                    "password": self.cred.password.get_secret_value(),
                    "global_delay_factor": 0.2,
                }
                logger.debug(f"Local binding: localhost:{tunnel.local_bind_port}")
                try:
                    logger.debug(
                        "Connecting to {dev} via Netmiko library...".format(
                            dev=self.device_config.location
                        )
                    )
                    nm_connect_direct = ConnectHandler(**scrape_host)
                    response = nm_connect_direct.send_command(self.query)
                except (
                    OSError,
                    NetMikoTimeoutException,
                    NetmikoTimeoutError,
                    sshtunnel.BaseSSHTunnelForwarderError,
                ) as scrape_error:
                    logger.error(
                        f"Error connecting to device {self.device_config.location}"
                    )
                    raise ScrapeError(
                        params.messages.connection_error,
                        device=self.device_config.location,
                        proxy=self.device_config.proxy,
                        error=scrape_error,
                    ) from None
                except (NetMikoAuthenticationException, NetmikoAuthError) as auth_error:
                    logger.error(
                        f"Error authenticating to device {self.device_config.location}"
                    )
                    raise AuthError(
                        params.messages.connection_error,
                        device=self.device_config.location,
                        proxy=self.device_config.proxy,
                        error=auth_error,
                    ) from None
        else:
            scrape_host = {
                "host": self.device_config.address.compressed,
                "port": self.device_config.port,
                "device_type": self.device_config.nos,
                "username": self.cred.username,
                "password": self.cred.password.get_secret_value(),
                "global_delay_factor": 0.2,
            }
            try:
                logger.debug(
                    "Connecting to {dev} via Netmiko library...".format(
                        dev=self.device_config.location
                    )
                )
                logger.debug(f"Device Parameters: {scrape_host}")
                nm_connect_direct = ConnectHandler(**scrape_host)
                response = nm_connect_direct.send_command(self.query)
            except (
                OSError,
                NetMikoTimeoutException,
                NetmikoTimeoutError,
                sshtunnel.BaseSSHTunnelForwarderError,
            ) as scrape_error:
                logger.error(
                    f"Error connecting to device {self.device_config.location}"
                )
                raise ScrapeError(
                    params.messages.connection_error,
                    device=self.device_config.location,
                    proxy=None,
                    error=scrape_error,
                ) from None
            except (NetMikoAuthenticationException, NetmikoAuthError) as auth_error:
                logger.error(
                    f"Error authenticating to device {self.device_config.location}"
                )
                raise AuthError(
                    params.messages.connection_error,
                    device=self.device_config.location,
                    proxy=None,
                    error=auth_error,
                ) from None
        if not response:
            logger.error(f"No response from device {self.device_config.location}")
            raise ScrapeError(
                params.messages.connection_error,
                device=self.device_config.location,
                proxy=None,
                error="No response",
            )
        logger.debug(f"Output for query: {self.query}:\n{response}")
        return response

    async def rest(self):
        """Sends HTTP POST to router running a hyperglass API agent"""
        logger.debug(f"Query parameters: {self.query}")

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

        logger.debug(f"HTTP Headers: {headers}")
        logger.debug(f"URL endpoint: {endpoint}")

        try:
            http_client = httpx.AsyncClient()
            raw_response = await http_client.post(
                endpoint, headers=headers, json=self.query, timeout=7
            )
            response = raw_response.text

            logger.debug(f"HTTP status code: {raw_response.status_code}")
            logger.debug(f"Output for query {self.query}:\n{response}")
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
            OSError,
        ) as rest_error:
            logger.error(f"Error connecting to device {self.device_config.location}")
            raise RestError(
                params.messages.connection_error,
                device=self.device_config.location,
                error=rest_error,
            )
        return response


class Execute:
    """
    Ingests raw user input, performs validation of target input, pulls
    all configuraiton variables for the input router and connects to the
    selected device to execute the query.
    """

    def __init__(self, lg_data):
        self.query_data = lg_data
        self.query_location = self.query_data["location"]
        self.query_type = self.query_data["query_type"]
        self.query_target = self.query_data["target"]

    def parse(self, raw_output, nos):
        """
        Deprecating: see #16

        Splits BGP raw output by AFI, returns only IPv4 & IPv6 output for
        protocol-agnostic commands (Community & AS_PATH Lookups).
        """
        logger.debug("Parsing raw output...")

        parsed = raw_output
        if self.query_type in ("bgp_community", "bgp_aspath"):
            logger.debug(f"Parsing raw output for device type {nos}")
            if nos in ("cisco_ios",):
                delimiter = "For address family: "
                parsed_raw = raw_output.split(delimiter)[1:3]
                parsed = "\n\n".join([delimiter + afi.rstrip() for afi in parsed_raw])
            elif nos in ("cisco_xr",):
                delimiter = "Address Family: "
                parsed_raw = raw_output.split(delimiter)[1:3]
                parsed = "\n\n".join([delimiter + afi.rstrip() for afi in parsed_raw])
        return parsed

    async def response(self):
        """
        Initializes Execute.filter(), if input fails to pass filter,
        returns errors to front end. Otherwise, executes queries.
        """
        device_config = getattr(devices, self.query_location)

        logger.debug(f"Received query for {self.query_data}")
        logger.debug(f"Matched device config: {device_config}")

        # Run query parameters through validity checks
        validation = Validate(device_config, self.query_type, self.query_target)
        valid_input = validation.validate_query()
        if valid_input:
            logger.debug(f"Validation passed for query: {self.query_data}")
            pass

        connect = None
        output = params.messages.general

        transport = Supported.map_transport(device_config.nos)
        connect = Connect(device_config, self.query_type, self.query_target, transport)
        if Supported.is_rest(device_config.nos):
            output = await connect.rest()
        elif Supported.is_scrape(device_config.nos):
            output = await connect.scrape()

        return output
