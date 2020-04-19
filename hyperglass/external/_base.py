"""Session handler for RIPEStat Data API."""

# Standard Library
import re
import json as _json
import asyncio
from json import JSONDecodeError
from socket import gaierror

# Third Party
import httpx
from httpx.status_codes import StatusCode

# Project
from hyperglass.log import log
from hyperglass.util import make_repr, parse_exception
from hyperglass.exceptions import HyperglassError


def _prepare_dict(_dict):
    return _json.loads(_json.dumps(_dict, default=str))


def _parse_response(response):
    parsed = {}
    try:
        parsed = response.json()
    except JSONDecodeError:
        try:
            parsed = _json.loads(response)
        except JSONDecodeError:
            log.error("Error parsing JSON for response {}", repr(response))
            parsed = {"data": response.text}
    return parsed


class BaseExternal:
    """Base session handler."""

    def __init__(
        self, base_url, uri_prefix="", uri_suffix="", verify_ssl=True, timeout=10,
    ):
        """Initialize connection instance."""
        self.__name__ = self.name
        self.base_url = base_url.strip("/")
        self.uri_prefix = uri_prefix.strip("/")
        self.uri_suffix = uri_suffix.strip("/")
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self._session = httpx.AsyncClient(
            verify=self.verify_ssl, base_url=self.base_url, timeout=self.timeout
        )

    @classmethod
    def __init_subclass__(cls, name=None, **kwargs):
        """Set correct subclass name."""
        super().__init_subclass__(**kwargs)
        cls.name = name or cls.__name__

    async def __aenter__(self):
        """Test connection on entry."""
        available = await self._test()

        if available:
            log.debug("Initialized session with {}", self.base_url)
            return self
        else:
            raise self._exception(f"Unable to create session to {self.name}")

    async def __aexit__(self, exc_type=None, exc_value=None, traceback=None):
        """Close connection on exit."""
        log.debug("Closing session with {}", self.base_url)

        await self._session.aclose()
        return True

    def __repr__(self):
        """Return user friendly representation of instance."""
        return make_repr(self)

    def _exception(self, message, exc=None, level="warning", **kwargs):
        """Add stringified exception to message if passed."""
        if exc is not None:
            message = f"{str(message)}: {str(exc)}"

        return HyperglassError(message, str(level), **kwargs)

    async def _test(self):
        """Open a low-level connection to the base URL to ensure its port is open."""
        log.debug("Testing connection to {}", self.base_url)

        try:
            test_host = re.sub(r"http(s)?\:\/\/", "", self.base_url)
            _reader, _writer = await asyncio.open_connection(test_host, 443)

        except gaierror as err:
            raise self._exception(
                f"{self.name} appears to be unreachable", err
            ) from None

        if _reader or _writer:
            return True
        else:
            return False

    async def _request(  # noqa: C901
        self,
        method,
        endpoint,
        item=None,
        params=None,
        data=None,
        timeout=None,
        response_required=False,
    ):
        """Run HTTP POST operation."""

        supported_methods = ("GET", "POST", "PUT", "DELETE", "HEAD", "PATCH")

        if method.upper() not in supported_methods:
            raise self._exception(
                f'Method must be one of {", ".join(supported_methods)}. '
                f"Got: {str(method)}"
            )

        endpoint = "/".join(
            i
            for i in (
                "",
                self.uri_prefix.strip("/"),
                endpoint.strip("/"),
                self.uri_suffix.strip("/"),
                item,
            )
            if i
        )

        request = {
            "method": method,
            "url": endpoint,
        }

        if params is not None:
            params = {str(k): str(v) for k, v in params.items() if v is not None}
            request["params"] = params

        if data is not None:
            if not isinstance(data, dict):
                raise self._exception(f"Data must be a dict, got: {str(data)}")
            request["json"] = _prepare_dict(data)

        if timeout is not None:
            if not isinstance(timeout, int):
                try:
                    timeout = int(timeout)
                except TypeError:
                    raise self._exception(
                        f"Timeout must be an int, got: {str(timeout)}"
                    )
            request["timeout"] = timeout

        log.debug("Constructed url {}", "".join((self.base_url, endpoint)))
        log.debug("Constructed request parameters {}", request)

        try:
            response = await self._session.request(**request)

            if response.status_code not in range(200, 300):
                status = StatusCode(response.status_code)
                error = _parse_response(response)
                raise self._exception(
                    f'{status.name.replace("_", " ")}: {error}', level="danger"
                ) from None

        except httpx.HTTPError as http_err:
            raise self._exception(parse_exception(http_err), level="danger") from None

        return _parse_response(response)

    async def _get(self, endpoint, **kwargs):
        return await self._request(method="GET", endpoint=endpoint, **kwargs)

    async def _post(self, endpoint, **kwargs):
        return await self._request(method="POST", endpoint=endpoint, **kwargs)

    async def _put(self, endpoint, **kwargs):
        return await self._request(method="PUT", endpoint=endpoint, **kwargs)

    async def _delete(self, endpoint, **kwargs):
        return await self._request(method="DELETE", endpoint=endpoint, **kwargs)

    async def _patch(self, endpoint, **kwargs):
        return await self._request(method="PATCH", endpoint=endpoint, **kwargs)

    async def _head(self, endpoint, **kwargs):
        return await self._request(method="HEAD", endpoint=endpoint, **kwargs)
