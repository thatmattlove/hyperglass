"""Execute validated & constructed query on device.

Accepts input from front end application, validates the input and
returns errors if input is invalid. Passes validated parameters to
construct.py, which is used to build & run the Netmiko connections or
hyperglass-frr API calls, returns the output back to the front end.
"""

# Standard Library
import math
import signal
from ssl import CertificateError

# Third Party
import httpx
from netmiko import (
    ConnectHandler,
    NetmikoAuthError,
    NetmikoTimeoutError,
    NetMikoTimeoutException,
    NetMikoAuthenticationException,
)

# Project
from hyperglass.log import log
from hyperglass.util import validate_nos, parse_exception
from hyperglass.compat import _sshtunnel as sshtunnel
from hyperglass.encode import jwt_decode, jwt_encode
from hyperglass.exceptions import (
    AuthError,
    RestError,
    ConfigError,
    ScrapeError,
    DeviceTimeout,
    ResponseEmpty,
)
from hyperglass.parsing.nos import nos_parsers
from hyperglass.configuration import params, devices
from hyperglass.parsing.common import parsers
from hyperglass.execution.construct import Construct


class Connect:
    """Connect to target device via specified transport.

    scrape_direct() directly connects to devices via SSH

    scrape_proxied() connects to devices via an SSH proxy

    rest() connects to devices via HTTP for RESTful API communication
    """

    def __init__(self, device, query_data, transport):
        """Initialize connection to device.

        Arguments:
            device {object} -- Matched device object
            query_data {object} -- Query object
            transport {str} -- 'scrape' or 'rest'
        """
        self.device = device
        self.query_data = query_data
        self.query_type = self.query_data.query_type
        self.query_target = self.query_data.query_target
        self.transport = transport
        self._query = Construct(device=self.device, query_data=self.query_data)
        self.query = self._query.queries()
        self.netmiko_args = {
            "global_delay_factor": params.netmiko_delay_factor,
            "timeout": math.floor(params.request_timeout * 1.25),
            "session_timeout": math.ceil(params.request_timeout - 1),
        }

    async def parsed_response(self, output):
        """Send output through common parsers.

        Arguments:
            output {str} -- Raw output

        Returns:
            {str} -- Parsed output
        """
        log.debug(f"Pre-parsed responses:\n{output}")
        parsed = ()
        if not self.device.structured_output:
            for coro in parsers:
                for response in output:
                    _output = await coro(commands=self.query, output=response)
                    parsed += (_output,)
            response = "\n\n".join(parsed)
        elif (
            self.device.structured_output
            and self.device.nos in nos_parsers.keys()
            and self.query_type in nos_parsers[self.device.nos].keys()
        ):
            func = nos_parsers[self.device.nos][self.query_type]
            response = func(output)
        log.debug(f"Post-parsed responses:\n{response}")
        return response

    async def scrape_proxied(self):
        """Connect to a device via an SSH proxy.

        Connects to the router via Netmiko library via the sshtunnel
        library, returns the command output.
        """
        log.debug(f"Connecting to {self.device.proxy} via sshtunnel library...")
        try:
            tunnel = sshtunnel.open_tunnel(
                self.device.proxy.address,
                self.device.proxy.port,
                ssh_username=self.device.proxy.credential.username,
                ssh_password=self.device.proxy.credential.password.get_secret_value(),
                remote_bind_address=(self.device.address, self.device.port),
                local_bind_address=("localhost", 0),
                skip_tunnel_checkup=False,
                gateway_timeout=params.request_timeout - 2,
            )
        except sshtunnel.BaseSSHTunnelForwarderError as scrape_proxy_error:
            log.error(
                f"Error connecting to device {self.device.name} via "
                f"proxy {self.device.proxy.name}"
            )
            raise ScrapeError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                proxy=self.device.proxy.name,
                error=str(scrape_proxy_error),
            )

        def handle_timeout(*args, **kwargs):
            tunnel.close()
            raise DeviceTimeout(
                params.messages.connection_error,
                device_name=self.device.display_name,
                proxy=self.device.proxy.name,
                error=params.messages.request_timeout,
            )

        signal.signal(signal.SIGALRM, handle_timeout)
        signal.alarm(params.request_timeout - 1)

        with tunnel:
            log.debug(
                "Established tunnel with {d}. Local bind port: {p}",
                d=self.device.proxy,
                p=tunnel.local_bind_port,
            )
            scrape_host = {
                "host": "localhost",
                "port": tunnel.local_bind_port,
                "device_type": self.device.nos,
                "username": self.device.credential.username,
                "password": self.device.credential.password.get_secret_value(),
                **self.netmiko_args,
            }

            try:
                log.debug("Connecting to {loc}...", loc=self.device.name)

                nm_connect_direct = ConnectHandler(**scrape_host)

                responses = ()
                for query in self.query:
                    raw = nm_connect_direct.send_command(query)
                    responses += (raw,)
                    log.debug(f'Raw response for command "{query}":\n{raw}')

                nm_connect_direct.disconnect()

            except (NetMikoTimeoutException, NetmikoTimeoutError) as scrape_error:
                log.error(
                    "Timeout connecting to device {loc}: {e}",
                    loc=self.device.name,
                    e=str(scrape_error),
                )
                raise DeviceTimeout(
                    params.messages.connection_error,
                    device_name=self.device.display_name,
                    proxy=self.device.proxy.name,
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
                    proxy=self.device.proxy.name,
                    error=params.messages.authentication_error,
                ) from None
            except sshtunnel.BaseSSHTunnelForwarderError:
                raise ScrapeError(
                    params.messages.connection_error,
                    device_name=self.device.display_name,
                    proxy=self.device.proxy.name,
                    error=params.messages.general,
                )
        if not responses:
            raise ScrapeError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                proxy=None,
                error=params.messages.no_response,
            )
        signal.alarm(0)
        return await self.parsed_response(responses)

    async def scrape_direct(self):
        """Connect directly to a device.

        Directly connects to the router via Netmiko library, returns the
        command output.
        """
        log.debug(f"Connecting directly to {self.device.name}...")

        scrape_host = {
            "host": self.device.address,
            "port": self.device.port,
            "device_type": self.device.nos,
            "username": self.device.credential.username,
            "password": self.device.credential.password.get_secret_value(),
            **self.netmiko_args,
        }

        try:
            nm_connect_direct = ConnectHandler(**scrape_host)

            def handle_timeout(*args, **kwargs):
                nm_connect_direct.disconnect()
                raise DeviceTimeout(
                    params.messages.connection_error,
                    device_name=self.device.display_name,
                    error=params.messages.request_timeout,
                )

            signal.signal(signal.SIGALRM, handle_timeout)
            signal.alarm(params.request_timeout - 1)

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
        signal.alarm(0)
        return await self.parsed_response(responses)

    async def rest(self):  # noqa: C901
        """Connect to a device running hyperglass-agent via HTTP."""
        log.debug(f"Query parameters: {self.query}")

        client_params = {
            "headers": {"Content-Type": "application/json"},
            "timeout": params.request_timeout,
        }
        if self.device.ssl is not None and self.device.ssl.enable:
            with self.device.ssl.cert.open("r") as file:
                cert = file.read()
                if not cert:
                    raise RestError(
                        "SSL Certificate for device {d} has not been imported",
                        level="danger",
                        d=self.device.display_name,
                    )
            http_protocol = "https"
            client_params.update({"verify": str(self.device.ssl.cert)})
            log.debug(
                (
                    f"Using {str(self.device.ssl.cert)} to validate connection "
                    f"to {self.device.name}"
                )
            )
        else:
            http_protocol = "http"
        endpoint = "{protocol}://{address}:{port}/query/".format(
            protocol=http_protocol, address=self.device.address, port=self.device.port
        )

        log.debug(f"URL endpoint: {endpoint}")

        try:
            async with httpx.AsyncClient(**client_params) as http_client:
                responses = ()

                for query in self.query:
                    encoded_query = await jwt_encode(
                        payload=query,
                        secret=self.device.credential.password.get_secret_value(),
                        duration=params.request_timeout,
                    )
                    log.debug(f"Encoded JWT: {encoded_query}")

                    raw_response = await http_client.post(
                        endpoint, json={"encoded": encoded_query}
                    )
                    log.debug(f"HTTP status code: {raw_response.status_code}")

                    raw = raw_response.text
                    log.debug(f"Raw Response: {raw}")

                    if raw_response.status_code == 200:
                        decoded = await jwt_decode(
                            payload=raw_response.json()["encoded"],
                            secret=self.device.credential.password.get_secret_value(),
                        )
                        log.debug(f"Decoded Response: {decoded}")
                        responses += (decoded,)

                    else:
                        log.error(raw_response.text)

        except httpx.exceptions.HTTPError as rest_error:
            msg = parse_exception(rest_error)
            log.error(f"Error connecting to device {self.device.name}: {msg}")
            raise RestError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                error=msg,
            )
        except OSError as ose:
            log.critical(str(ose))
            raise RestError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                error="System error",
            )
        except CertificateError as cert_error:
            log.critical(str(cert_error))
            msg = parse_exception(cert_error)
            raise RestError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                error=f"{msg}: {cert_error}",
            )

        if raw_response.status_code != 200:
            log.error(f"Response code is {raw_response.status_code}")
            raise RestError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                error=params.messages.general,
            )

        if not responses:
            log.error(f"No response from device {self.device.name}")
            raise RestError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                error=params.messages.no_response,
            )

        return await self.parsed_response(responses)


class Execute:
    """Perform query execution on device.

    Ingests raw user input, performs validation of target input, pulls
    all configuration variables for the input router and connects to the
    selected device to execute the query.
    """

    def __init__(self, lg_data):
        """Initialize execution object.

        Arguments:
            lg_data {object} -- Validated query object
        """
        self.query_data = lg_data
        self.query_location = self.query_data.query_location
        self.query_type = self.query_data.query_type
        self.query_target = self.query_data.query_target

    async def response(self):
        """Initiate query validation and execution."""
        device = getattr(devices, self.query_location)

        log.debug(f"Received query for {self.query_data}")
        log.debug(f"Matched device config: {device}")

        supported, transport = validate_nos(device.nos)

        connect = None
        output = params.messages.general
        connect = Connect(device, self.query_data, transport)

        if supported and transport == "rest":
            output = await connect.rest()

        elif supported and transport == "scrape":
            if device.proxy:
                output = await connect.scrape_proxied()
            else:
                output = await connect.scrape_direct()
        else:
            raise ConfigError('"{nos}" is not supported.', nos=device.nos)

        if output == "" or output == "\n":
            raise ResponseEmpty(
                params.messages.no_output, device_name=device.display_name
            )

        log.debug(f"Output for query: {self.query_data.json()}:\n{repr(output)}")

        return output
