"""Execute validated & constructed query on device.

Accepts input from front end application, validates the input and
returns errors if input is invalid. Passes validated parameters to
construct.py, which is used to build & run the Netmiko connections or
hyperglass-frr API calls, returns the output back to the front end.
"""

# Standard Library
from ssl import CertificateError
from typing import Iterable

# Third Party
import httpx

# Project
from hyperglass.log import log
from hyperglass.util import parse_exception
from hyperglass.encode import jwt_decode, jwt_encode
from hyperglass.exceptions import RestError, ResponseEmpty
from hyperglass.configuration import params

# Local
from ._common import Connection


class AgentConnection(Connection):
    """Connect to target device via hyperglass-agent."""

    async def collect(self) -> Iterable:  # noqa: C901
        """Connect to a device running hyperglass-agent via HTTP."""
        log.debug("Query parameters: {}", self.query)

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
            protocol=http_protocol, address=self.device._target, port=self.device.port
        )

        log.debug("URL endpoint: {}", endpoint)

        try:
            async with httpx.AsyncClient(**client_params) as http_client:
                responses = ()

                for query in self.query:
                    encoded_query = await jwt_encode(
                        payload=query,
                        secret=self.device.credential.password.get_secret_value(),
                        duration=params.request_timeout,
                    )
                    log.debug("Encoded JWT: {}", encoded_query)

                    raw_response = await http_client.post(
                        endpoint, json={"encoded": encoded_query}
                    )
                    log.debug("HTTP status code: {}", raw_response.status_code)

                    raw = raw_response.text
                    log.debug("Raw Response:\n{}", raw)

                    if raw_response.status_code == 200:
                        decoded = await jwt_decode(
                            payload=raw_response.json()["encoded"],
                            secret=self.device.credential.password.get_secret_value(),
                        )
                        log.debug("Decoded Response:\n{}", decoded)
                        responses += (decoded,)

                    elif raw_response.status_code == 204:
                        raise ResponseEmpty(
                            params.messages.no_output,
                            device_name=self.device.display_name,
                        )

                    else:
                        log.error(raw_response.text)

        except httpx.exceptions.HTTPError as rest_error:
            msg = parse_exception(rest_error)
            log.error("Error connecting to device {}: {}", self.device.name, msg)
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
            log.error("Response code is {}", raw_response.status_code)
            raise RestError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                error=params.messages.general,
            )

        if not responses:
            log.error("No response from device {}", self.device.name)
            raise RestError(
                params.messages.connection_error,
                device_name=self.device.display_name,
                error=params.messages.no_response,
            )

        return responses
