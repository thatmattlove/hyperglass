"""Execute validated & constructed query on device.

Accepts input from front end application, validates the input and
returns errors if input is invalid. Passes validated parameters to
construct.py, which is used to build & run the Netmiko connections or
hyperglass-frr API calls, returns the output back to the front end.
"""

# Standard Library
from ssl import CertificateError
from typing import TYPE_CHECKING, Iterable

# Third Party
import httpx

# Project
from hyperglass.log import log
from hyperglass.util import parse_exception
from hyperglass.encode import jwt_decode, jwt_encode
from hyperglass.configuration import params
from hyperglass.exceptions.public import RestError, ResponseEmpty

# Local
from ._common import Connection

if TYPE_CHECKING:
    # Project
    from hyperglass.compat._sshtunnel import SSHTunnelForwarder


class AgentConnection(Connection):
    """Connect to target device via hyperglass-agent."""

    def setup_proxy(self: "Connection") -> "SSHTunnelForwarder":
        """Return a preconfigured sshtunnel.SSHTunnelForwarder instance."""
        raise NotImplementedError("AgentConnection does not implement an SSH proxy.")

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
                        d=self.device.name,
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
                        raise ResponseEmpty(query=self.query_data)

                    else:
                        log.error(raw_response.text)

        except httpx.exceptions.HTTPError as rest_error:
            msg = parse_exception(rest_error)
            raise RestError(error=httpx.exceptions.HTTPError(msg), device=self.device)

        except OSError as ose:
            raise RestError(error=ose, device=self.device)

        except CertificateError as cert_error:
            msg = parse_exception(cert_error)
            raise RestError(error=CertificateError(cert_error), device=self.device)

        if raw_response.status_code != 200:
            raise RestError(
                error=ConnectionError(f"Response code {raw_response.status_code}"),
                device=self.device,
            )

        if not responses:
            raise ResponseEmpty(query=self.query_data)

        return responses
