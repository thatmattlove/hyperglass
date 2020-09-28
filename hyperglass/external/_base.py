"""Session handler for RIPEStat Data API."""

# Standard Library
import re
import json as _json
import socket
from json import JSONDecodeError
from socket import gaierror

# Third Party
import httpx
from httpx.status_codes import StatusCode

# Project
from hyperglass.log import log
from hyperglass.util import make_repr, parse_exception
from hyperglass.constants import __version__
from hyperglass.exceptions import HyperglassError


def _prepare_dict(_dict):
    return _json.loads(_json.dumps(_dict, default=str))


class BaseExternal:
    """Base session handler."""

    def __init__(
        self,
        base_url,
        config=None,
        uri_prefix="",
        uri_suffix="",
        verify_ssl=True,
        timeout=10,
        parse=True,
    ):
        """Initialize connection instance."""
        self.__name__ = getattr(self, "name", "BaseExternal")
        self.config = config
        self.base_url = base_url.strip("/")
        self.uri_prefix = uri_prefix.strip("/")
        self.uri_suffix = uri_suffix.strip("/")
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.parse = parse

        session_args = {
            "verify": self.verify_ssl,
            "base_url": self.base_url,
            "timeout": self.timeout,
        }
        self._session = httpx.Client(**session_args)
        self._asession = httpx.AsyncClient(**session_args)

    @classmethod
    def __init_subclass__(cls, name=None, **kwargs):
        """Set correct subclass name."""
        super().__init_subclass__(**kwargs)
        cls.name = name or cls.__name__

    async def __aenter__(self):
        """Test connection on entry."""
        available = await self._atest()

        if available:
            log.debug("Initialized session with {}", self.base_url)
            return self
        else:
            raise self._exception(f"Unable to create session to {self.name}")

    async def __aexit__(self, exc_type=None, exc_value=None, traceback=None):
        """Close connection on exit."""
        log.debug("Closing session with {}", self.base_url)

        await self._asession.aclose()
        return True

    def __enter__(self):
        """Test connection on entry."""
        available = self._test()

        if available:
            log.debug("Initialized session with {}", self.base_url)
            return self
        else:
            raise self._exception(f"Unable to create session to {self.name}")

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        """Close connection on exit."""
        if exc_type is not None:
            log.error(traceback)
        self._session.close()

    def __repr__(self):
        """Return user friendly representation of instance."""
        return make_repr(self)

    def _exception(self, message, exc=None, level="warning", **kwargs):
        """Add stringified exception to message if passed."""
        if exc is not None:
            message = f"{str(message)}: {str(exc)}"

        return HyperglassError(message, str(level), **kwargs)

    def _parse_response(self, response):
        if self.parse:
            parsed = {}
            try:
                parsed = response.json()
            except JSONDecodeError:
                try:
                    parsed = _json.loads(response)
                except (JSONDecodeError, TypeError):
                    log.error("Error parsing JSON for response {}", repr(response))
                    parsed = {"data": response.text}
        else:
            parsed = response
        return parsed

    def _test(self):
        """Open a low-level connection to the base URL to ensure its port is open."""
        log.debug("Testing connection to {}", self.base_url)

        try:
            # Parse out just the hostname from a URL string.
            # E.g. `https://www.example.com` becomes `www.example.com`
            test_host = re.sub(r"http(s)?\:\/\/", "", self.base_url)

            # Create a generic socket object
            test_socket = socket.socket()

            # Try opening a low-level socket to make sure it's even
            # listening on the port prior to trying to use it.
            test_socket.connect((test_host, 443))

            # Properly shutdown & close the socket.
            test_socket.shutdown(1)
            test_socket.close()

        except gaierror as err:
            # Raised if the target isn't listening on the port
            raise self._exception(
                f"{self.name} appears to be unreachable", err
            ) from None

        return True

    async def _atest(self):
        """Open a low-level connection to the base URL to ensure its port is open."""
        return self._test()

    def _build_request(self, **kwargs):
        """Process requests parameters into structure usable by http library."""
        # Standard Library
        from operator import itemgetter

        supported_methods = ("GET", "POST", "PUT", "DELETE", "HEAD", "PATCH")

        (
            method,
            endpoint,
            item,
            headers,
            params,
            data,
            timeout,
            response_required,
        ) = itemgetter(*kwargs.keys())(kwargs)

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
            "headers": {"user-agent": f"hyperglass/{__version__}"},
        }

        if headers is not None:
            request.update({"headers": headers})

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

        log.debug("Constructed request parameters {}", request)
        return request

    async def _arequest(  # noqa: C901
        self,
        method,
        endpoint,
        item=None,
        headers=None,
        params=None,
        data=None,
        timeout=None,
        response_required=False,
    ):
        """Run HTTP POST operation."""
        request = self._build_request(
            method=method,
            endpoint=endpoint,
            item=item,
            headers=None,
            params=params,
            data=data,
            timeout=timeout,
            response_required=response_required,
        )

        try:
            response = await self._asession.request(**request)

            if response.status_code not in range(200, 300):
                status = StatusCode(response.status_code)
                error = self._parse_response(response)
                raise self._exception(
                    f'{status.name.replace("_", " ")}: {error}', level="danger"
                ) from None

        except httpx.HTTPError as http_err:
            raise self._exception(parse_exception(http_err), level="danger") from None

        return self._parse_response(response)

    async def _aget(self, endpoint, **kwargs):
        return await self._arequest(method="GET", endpoint=endpoint, **kwargs)

    async def _apost(self, endpoint, **kwargs):
        return await self._arequest(method="POST", endpoint=endpoint, **kwargs)

    async def _aput(self, endpoint, **kwargs):
        return await self._arequest(method="PUT", endpoint=endpoint, **kwargs)

    async def _adelete(self, endpoint, **kwargs):
        return await self._arequest(method="DELETE", endpoint=endpoint, **kwargs)

    async def _apatch(self, endpoint, **kwargs):
        return await self._arequest(method="PATCH", endpoint=endpoint, **kwargs)

    async def _ahead(self, endpoint, **kwargs):
        return await self._arequest(method="HEAD", endpoint=endpoint, **kwargs)

    def _request(  # noqa: C901
        self,
        method,
        endpoint,
        item=None,
        headers=None,
        params=None,
        data=None,
        timeout=None,
        response_required=False,
    ):
        """Run HTTP POST operation."""
        request = self._build_request(
            method=method,
            endpoint=endpoint,
            item=item,
            headers=None,
            params=params,
            data=data,
            timeout=timeout,
            response_required=response_required,
        )

        try:
            response = self._session.request(**request)

            if response.status_code not in range(200, 300):
                status = StatusCode(response.status_code)
                error = self._parse_response(response)
                raise self._exception(
                    f'{status.name.replace("_", " ")}: {error}', level="danger"
                ) from None

        except httpx.HTTPError as http_err:
            raise self._exception(parse_exception(http_err), level="danger") from None

        return self._parse_response(response)

    def _get(self, endpoint, **kwargs):
        return self._request(method="GET", endpoint=endpoint, **kwargs)

    def _post(self, endpoint, **kwargs):
        return self._request(method="POST", endpoint=endpoint, **kwargs)

    def _put(self, endpoint, **kwargs):
        return self._request(method="PUT", endpoint=endpoint, **kwargs)

    def _delete(self, endpoint, **kwargs):
        return self._request(method="DELETE", endpoint=endpoint, **kwargs)

    def _patch(self, endpoint, **kwargs):
        return self._request(method="PATCH", endpoint=endpoint, **kwargs)

    def _head(self, endpoint, **kwargs):
        return self._request(method="HEAD", endpoint=endpoint, **kwargs)
