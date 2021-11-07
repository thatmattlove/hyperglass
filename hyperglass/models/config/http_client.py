"""Configuration models for hyperglass http client."""

# Standard Library
import typing as t

# Third Party
import httpx
from pydantic import (
    FilePath,
    SecretStr,
    StrictInt,
    StrictStr,
    StrictBool,
    PrivateAttr,
    IPvAnyAddress,
)

# Project
from hyperglass.models import HyperglassModel
from hyperglass.constants import __version__

# Local
from ..fields import IntFloat, HttpMethod, Primitives

if t.TYPE_CHECKING:
    # Local
    from .devices import Device

DEFAULT_QUERY_PARAMETERS: t.Dict[str, str] = {
    "query_target": "{query_target}",
    "query_type": "{query_type}",
    "query_location": "{query_location}",
}

BodyFormat = t.Literal["json", "yaml", "xml", "text"]
Scheme = t.Literal["http", "https"]


class AttributeMapConfig(HyperglassModel):
    """Allow the user to 'rewrite' hyperglass field names to their own values."""

    query_target: t.Optional[StrictStr]
    query_type: t.Optional[StrictStr]
    query_location: t.Optional[StrictStr]


class AttributeMap(HyperglassModel):
    """Merged implementation of attribute map configuration."""

    query_target: StrictStr
    query_type: StrictStr
    query_location: StrictStr


class HttpBasicAuth(HyperglassModel):
    """Configuration model for HTTP basic authentication."""

    username: StrictStr
    password: SecretStr


class HttpConfiguration(HyperglassModel):
    """HTTP client configuration."""

    _attribute_map: AttributeMap = PrivateAttr()
    path: StrictStr = "/"
    method: HttpMethod = "GET"
    scheme: Scheme = "https"
    query: t.Optional[t.Union[t.Literal[False], t.Dict[str, Primitives]]]
    verify_ssl: StrictBool = True
    ssl_ca: t.Optional[FilePath]
    ssl_client: t.Optional[FilePath]
    source: t.Optional[IPvAnyAddress]
    timeout: IntFloat = 5
    headers: t.Dict[str, str] = {}
    follow_redirects: StrictBool = False
    basic_auth: t.Optional[HttpBasicAuth]
    attribute_map: AttributeMapConfig = AttributeMapConfig()
    body_format: BodyFormat = "json"
    retries: StrictInt = 0

    def __init__(self, **data: t.Any) -> None:
        """Create HTTP Client Configuration Definition."""

        super().__init__(**data)
        self._attribute_map = self._create_attribute_map()

    def _create_attribute_map(self) -> AttributeMap:
        """Create AttributeMap instance with defined overrides."""

        return AttributeMap(
            query_location=self.attribute_map.query_location or "query_location",
            query_type=self.attribute_map.query_type or "query_type",
            query_target=self.attribute_map.query_target or "query_target",
        )

    def create_client(self, *, device: "Device") -> httpx.AsyncClient:
        """Create a pre-configured http client."""

        # Use the CA certificates for SSL verification, if present.
        verify = self.verify_ssl
        if self.ssl_ca is not None:
            verify = httpx.create_ssl_context(verify=str(self.ssl_ca))

        transport_constructor = {"retries": self.retries}

        # Use `source` IP address as httpx transport's `local_address`, if defined.
        if self.source is not None:
            transport_constructor["local_address"] = str(self.source)

        transport = httpx.AsyncHTTPTransport(**transport_constructor)

        # Add the port to the URL only if it is not 22, 80, or 443.
        base_url = f"{self.scheme}://{device.address!s}".strip("/")
        if device.port not in (22, 80, 443):
            base_url += f":{device.port!s}"

        parameters = {
            "verify": verify,
            "transport": transport,
            "timeout": self.timeout,
            "follow_redirects": self.follow_redirects,
            "base_url": f"{self.scheme}://{device.address!s}".strip("/"),
            "headers": {"user-agent": f"hyperglass/{__version__}", **self.headers},
        }

        # Use client certificate authentication, if defined.
        if self.ssl_client is not None:
            parameters["cert"] = str(self.ssl_client)

        # Use basic authentication, if defined.
        if self.basic_auth is not None:
            parameters["auth"] = httpx.BasicAuth(
                username=self.basic_auth.username,
                password=self.basic_auth.password.get_secret_value(),
            )

        return httpx.AsyncClient(**parameters)
