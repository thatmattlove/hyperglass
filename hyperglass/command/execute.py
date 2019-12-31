"""Execute validated & constructed query on device.

Accepts input from front end application, validates the input and
returns errors if input is invalid. Passes validated parameters to
construct.py, which is used to build & run the Netmiko connectoins or
hyperglass-frr API calls, returns the output back to the front end.
"""

# Standard Library Imports
import re

# Third Party Imports
import httpx
import sshtunnel
from netmiko import ConnectHandler
from netmiko import NetMikoAuthenticationException
from netmiko import NetmikoAuthError
from netmiko import NetmikoTimeoutError
from netmiko import NetMikoTimeoutException

# Project Imports
from hyperglass.command.construct import Construct
from hyperglass.command.encode import jwt_decode
from hyperglass.command.encode import jwt_encode
from hyperglass.command.validate import Validate
from hyperglass.configuration import devices
from hyperglass.configuration import params
from hyperglass.constants import Supported
from hyperglass.constants import protocol_map
from hyperglass.exceptions import AuthError
from hyperglass.exceptions import DeviceTimeout
from hyperglass.exceptions import ResponseEmpty
from hyperglass.exceptions import RestError
from hyperglass.exceptions import ScrapeError
from hyperglass.util import log


class Connect:
    """
    Parent class for all connection types:

    scrape_direct() directly connects to devices via SSH

    scrape_proxied() connects to devices via an SSH proxy

    rest() connects to devices via HTTP for RESTful API communication
    """

    def __init__(self, device, query_data, transport):
        self.device = device
        self.query_data = query_data
        self.query_type = self.query_data["query_type"]
        self.query_target = self.query_data["query_target"]
        self.transport = transport
        self.query = getattr(
            Construct(
                device=self.device, query_data=self.query_data, transport=self.transport
            ),
            self.query_type,
        )()

    async def scrape_proxied(self):
        """
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
            )
        except sshtunnel.BaseSSHTunnelForwarderError as scrape_proxy_error:
            log.error(
                f"Error connecting to device {self.device.location} via "
                f"proxy {self.device.proxy.name}"
            )
            raise ScrapeError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                proxy=self.device.proxy.name,
                error=scrape_proxy_error,
            )
        with tunnel:
            log.debug(f"Established tunnel with {self.device.proxy}")
            scrape_host = {
                "host": "localhost",
                "port": tunnel.local_bind_port,
                "device_type": self.device.nos,
                "username": self.device.credential.username,
                "password": self.device.credential.password.get_secret_value(),
                "global_delay_factor": 0.2,
                "timeout": params.general.request_timeout - 1,
            }
            log.debug(f"SSH proxy local binding: localhost:{tunnel.local_bind_port}")
            try:
                log.debug(
                    f"Connecting to {self.device.location} " "via Netmiko library..."
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
                    f"Timeout connecting to device {self.device.location}: "
                    f"{scrape_error}"
                )
                raise DeviceTimeout(
                    params.messages.connection_error,
                    device_name=self.device.display_name,
                    proxy=self.device.proxy.name,
                    error=params.messages.request_timeout,
                )
            except (NetMikoAuthenticationException, NetmikoAuthError) as auth_error:
                log.error(
                    f"Error authenticating to device {self.device.location}: "
                    f"{auth_error}"
                )
                raise AuthError(
                    params.messages.connection_error,
                    device_name=self.device.display_name,
                    proxy=self.device.proxy.name,
                    error=params.messages.authentication_error,
                ) from None
            except sshtunnel.BaseSSHTunnelForwarderError as scrape_error:
                log.error(
                    f"Error connecting to device proxy {self.device.proxy}: "
                    f"{scrape_error}"
                )
                raise ScrapeError(
                    params.messages.connection_error,
                    device_name=self.device.display_name,
                    proxy=self.device.proxy.name,
                    error=params.messages.general,
                )
        if response is None:
            log.error(f"No response from device {self.device.location}")
            raise ScrapeError(
                params.messages.connection_error,
                device_name=self.device.display_name,
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

        log.debug(f"Connecting directly to {self.device.location}...")

        scrape_host = {
            "host": self.device.address,
            "port": self.device.port,
            "device_type": self.device.nos,
            "username": self.device.credential.username,
            "password": self.device.credential.password.get_secret_value(),
            "global_delay_factor": 0.2,
            "timeout": params.general.request_timeout - 1,
        }

        try:
            log.debug(f"Device Parameters: {scrape_host}")
            log.debug(f"Connecting to {self.device.location} via Netmiko library")
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
                device_name=self.device.display_name,
                proxy=None,
                error=params.messages.request_timeout,
            )
        except (NetMikoAuthenticationException, NetmikoAuthError) as auth_error:
            log.error(f"Error authenticating to device {self.device.location}")
            log.error(auth_error)

            raise AuthError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                proxy=None,
                error=params.messages.authentication_error,
            )
        if response is None:
            log.error(f"No response from device {self.device.location}")
            raise ScrapeError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                proxy=None,
                error=params.messages.noresponse_error,
            )
        log.debug(f"Output for query: {self.query}:\n{response}")
        return response

    async def rest(self):
        """Sends HTTP POST to router running a hyperglass API agent"""
        log.debug(f"Query parameters: {self.query}")

        headers = {"Content-Type": "application/json"}
        http_protocol = protocol_map.get(self.device.port, "https")
        endpoint = "{protocol}://{addr}:{port}/query".format(
            protocol=http_protocol, addr=self.device.address, port=self.device.port
        )

        log.debug(f"HTTP Headers: {headers}")
        log.debug(f"URL endpoint: {endpoint}")

        try:
            async with httpx.Client() as http_client:
                responses = []
                for query in self.query:
                    encoded_query = await jwt_encode(
                        payload=query,
                        secret=self.device.credential.password.get_secret_value(),
                        duration=params.general.request_timeout,
                    )
                    log.debug(f"Encoded JWT: {encoded_query}")
                    raw_response = await http_client.post(
                        endpoint,
                        headers=headers,
                        json={"encoded": encoded_query},
                        timeout=params.general.request_timeout,
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

                        responses.append(decoded)
                    else:
                        log.error(raw_response.text)

            response = "\n\n".join(responses)
            log.debug(f"Output for query {self.query}:\n{response}")
        except httpx.exceptions.HTTPError as rest_error:
            rest_msg = " ".join(
                re.findall(r"[A-Z][^A-Z]*", rest_error.__class__.__name__)
            )
            log.error(f"Error connecting to device {self.device.location}: {rest_msg}")
            raise RestError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                error=rest_msg,
            )
        except OSError:
            raise RestError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                error="System error",
            )

        if raw_response.status_code != 200:
            log.error(f"Response code is {raw_response.status_code}")
            raise RestError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                error=params.messages.general,
            )

        if not response:
            log.error(f"No response from device {self.device.location}")
            raise RestError(
                params.messages.connection_error,
                device_name=self.device.display_name,
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
        device = getattr(devices, self.query_location)

        log.debug(f"Received query for {self.query_data}")
        log.debug(f"Matched device config: {device}")

        # Run query parameters through validity checks
        validation = Validate(device, self.query_data, self.query_target)
        valid_input = validation.validate_query()
        if valid_input:
            log.debug(f"Validation passed for query: {self.query_data}")
            pass

        connect = None
        output = params.messages.general

        transport = Supported.map_transport(device.nos)
        connect = Connect(device, self.query_data, transport)

        if Supported.is_rest(device.nos):
            output = await connect.rest()
        elif Supported.is_scrape(device.nos):
            if device.proxy:
                output = await connect.scrape_proxied()
            else:
                output = await connect.scrape_direct()
        if output == "":
            raise ResponseEmpty(
                params.messages.no_output, device_name=device.display_name
            )
        return output
