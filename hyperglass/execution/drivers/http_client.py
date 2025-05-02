"""Interact with an http-based device."""

# Standard Library
import typing as t

# Third Party
import httpx

# Project
from hyperglass.util import get_fmt_keys
from hyperglass.exceptions.public import AuthError, RestError, DeviceTimeout, ResponseEmpty

# Local
from ._common import Connection

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.api import Query
    from hyperglass.models.config.devices import Device
    from hyperglass.models.config.http_client import HttpConfiguration


class HttpClient(Connection):
    """Interact with an http-based device."""

    config: "HttpConfiguration"
    client: httpx.AsyncClient

    def __init__(self, device: "Device", query_data: "Query") -> None:
        """Initialize base connection and set http config & client."""
        super().__init__(device, query_data)
        self.config = device.http
        self.client = self.config.create_client(device=device)

    def setup_proxy(self: "Connection"):
        """HTTP Client does not support SSH proxies."""
        raise NotImplementedError("HTTP Client does not support SSH proxies.")

    def _query_params(self) -> t.Dict[str, str]:
        if self.config.query is None:
            return {
                self.config._attribute_map.query_target: self.query_data.query_target,
                self.config._attribute_map.query_location: self.query_data.query_location,
                self.config._attribute_map.query_type: self.query_data.query_type,
            }
        if isinstance(self.config.query, t.Dict):
            return {
                key: value.format(
                    **{
                        str(v): str(getattr(self.query_data, k, None))
                        for k, v in self.config.attribute_map.model_dump().items()
                        if v in get_fmt_keys(value)
                    }
                )
                for key, value in self.config.query.items()
            }
        return {}

    def _body(self) -> t.Dict[str, t.Union[t.Dict[str, t.Any], str]]:
        data = {
            self.config._attribute_map.query_target: self.query_data.query_target,
            self.config._attribute_map.query_location: self.query_data.query_location,
            self.config._attribute_map.query_type: self.query_data.query_type,
        }
        if self.config.body_format == "json":
            return {"json": data}

        if self.config.body_format == "yaml":
            # Third Party
            import yaml

            return {"content": yaml.dump(data), "headers": {"content-type": "text/yaml"}}

        if self.config.body_format == "xml":
            # Third Party
            import xmltodict  # type: ignore

            return {
                "content": xmltodict.unparse({"query": data}),
                "headers": {"content-type": "application/xml"},
            }
        if self.config.body_format == "text":
            return {"data": data}

        return {}

    async def collect(self, *args: t.Any, **kwargs: t.Any) -> t.Iterable:
        """Collect response data from an HTTP endpoint."""

        query = self._query_params()
        responses = ()

        async with self.client as client:
            body = {}
            if self.config.method in ("POST", "PATCH", "PUT"):
                body = self._body()

            try:
                response: httpx.Response = await client.request(
                    method=self.config.method, url=self.config.path, params=query, **body
                )
                response.raise_for_status()
                data = response.text.strip()

                if len(data) == 0:
                    raise ResponseEmpty(query=self.query_data)

                responses += (data,)

            except httpx.TimeoutException as error:
                raise DeviceTimeout(error=error, device=self.device) from error

            except httpx.HTTPStatusError as error:
                if error.response.status_code == 401:
                    raise AuthError(error=error, device=self.device) from error
                raise RestError(error=error, device=self.device) from error
            return responses
