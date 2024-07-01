"""Session handler for external http data sources."""

# Standard Library
import re
import json as _json
import socket
import typing as t
from json import JSONDecodeError
from socket import gaierror

# Third Party
import httpx

# Project
from hyperglass.log import log
from hyperglass.util import parse_exception, repr_from_attrs
from hyperglass.settings import Settings
from hyperglass.constants import __version__
from hyperglass.models.fields import JsonValue, HttpMethod, Primitives
from hyperglass.exceptions.private import ExternalError

if t.TYPE_CHECKING:
    # Standard Library
    from types import TracebackType

    # Project
    from hyperglass.exceptions._common import ErrorLevel
    from hyperglass.models.config.logging import Http

D = t.TypeVar("D", bound=t.Dict)


def _prepare_dict(_dict: D) -> D:
    return _json.loads(_json.dumps(_dict, default=str))


class BaseExternal:
    """Base session handler."""

    def __init__(
        self,
        base_url: str,
        config: t.Optional["Http"] = None,
        uri_prefix: str = "",
        uri_suffix: str = "",
        verify_ssl: bool = True,
        timeout: int = 10,
        parse: bool = True,
    ) -> None:
        """Initialize connection instance."""
        self.__name__ = getattr(self, "name", "BaseExternal")
        self.name = self.__name__
        self.config = config
        self.base_url = base_url.strip("/")
        self.uri_prefix = uri_prefix.strip("/")
        self.uri_suffix = uri_suffix.strip("/")
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.parse = parse

        context = httpx.create_ssl_context(verify=verify_ssl)

        if Settings.ca_cert is not None:
            context.load_verify_locations(cafile=str(Settings.ca_cert))

        client_kwargs = {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "verify": context,
        }

        self._session = httpx.Client(**client_kwargs)
        self._asession = httpx.AsyncClient(**client_kwargs)

    @classmethod
    def __init_subclass__(
        cls: "BaseExternal", name: t.Optional[str] = None, **kwargs: t.Any
    ) -> None:
        """Set correct subclass name."""
        super().__init_subclass__(**kwargs)
        cls.name = name or cls.__name__

    async def __aenter__(self: "BaseExternal") -> "BaseExternal":
        """Test connection on entry."""
        available = await self._atest()

        if available:
            log.bind(url=self.base_url).debug("Initialized session")
            return self
        raise self._exception(f"Unable to create session to {self.name}")

    async def __aexit__(
        self: "BaseExternal",
        exc_type: t.Optional[t.Type[BaseException]] = None,
        exc_value: t.Optional[BaseException] = None,
        traceback: t.Optional["TracebackType"] = None,
    ) -> True:
        """Close connection on exit."""
        log.bind(url=self.base_url).debug("Closing session")

        if exc_type is not None:
            log.error(str(exc_value))

        await self._asession.aclose()
        if exc_value is not None:
            raise exc_value
        return True

    def __enter__(self: "BaseExternal") -> "BaseExternal":
        """Test connection on entry."""
        available = self._test()

        if available:
            log.bind(url=self.base_url).debug("Initialized session")
            return self
        raise self._exception(f"Unable to create session to {self.name}")

    def __exit__(
        self: "BaseExternal",
        exc_type: t.Optional[t.Type[BaseException]] = None,
        exc_value: t.Optional[BaseException] = None,
        exc_traceback: t.Optional["TracebackType"] = None,
    ) -> bool:
        """Close connection on exit."""
        if exc_type is not None:
            log.error(str(exc_value))
        self._session.close()
        if exc_value is not None:
            raise exc_value
        return True

    def __repr__(self: "BaseExternal") -> str:
        """Return user friendly representation of instance."""
        return repr_from_attrs(self, ("name", "base_url", "config", "parse"))

    def _exception(
        self: "BaseExternal",
        message: str,
        exc: t.Optional[BaseException] = None,
        level: "ErrorLevel" = "warning",
        **kwargs: t.Any,
    ) -> ExternalError:
        """Add stringified exception to message if passed."""
        if exc is not None:
            message = f"{message!s}: {exc!s}"

        return ExternalError(message=message, level=level, **kwargs)

    def _parse_response(self: "BaseExternal", response: httpx.Response) -> t.Any:
        if self.parse:
            parsed = {}
            try:
                parsed = response.json()
            except JSONDecodeError:
                try:
                    parsed = _json.loads(response)
                except (JSONDecodeError, TypeError):
                    parsed = {"data": response.text}
        else:
            parsed = response
        return parsed

    def _test(self: "BaseExternal") -> bool:
        """Open a low-level connection to the base URL to ensure its port is open."""
        log.bind(url=self.base_url).debug("Testing connection")

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
                f"{self.name!r} appears to be unreachable at {self.base_url!r}", err
            ) from None

        return True

    async def _atest(self: "BaseExternal") -> bool:
        """Open a low-level connection to the base URL to ensure its port is open."""
        return self._test()

    def _build_request(self: "BaseExternal", **kwargs: t.Any) -> t.Dict[str, t.Any]:
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
                f'Method must be one of {", ".join(supported_methods)}. ' f"Got: {str(method)}"
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
                except TypeError as err:
                    raise self._exception(f"Timeout must be an int, got: {str(timeout)}") from err
            request["timeout"] = timeout
        return request

    async def _arequest(  # noqa: C901
        self: "BaseExternal",
        method: HttpMethod,
        endpoint: str,
        item: t.Union[str, int, None] = None,
        headers: t.Dict[str, str] = None,
        params: t.Dict[str, JsonValue[Primitives]] = None,
        data: t.Optional[t.Any] = None,
        timeout: t.Optional[int] = None,
        response_required: bool = False,
    ) -> t.Any:
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
                status = httpx.codes(response.status_code)
                error = self._parse_response(response)
                raise self._exception(
                    f'{status.name.replace("_", " ")}: {error}', level="danger"
                ) from None

        except httpx.HTTPError as http_err:
            raise self._exception(parse_exception(http_err), level="danger") from None

        return self._parse_response(response)

    async def _aget(self: "BaseExternal", endpoint: str, **kwargs: t.Any) -> t.Any:
        return await self._arequest(method="GET", endpoint=endpoint, **kwargs)

    async def _apost(self: "BaseExternal", endpoint: str, **kwargs: t.Any) -> t.Any:
        return await self._arequest(method="POST", endpoint=endpoint, **kwargs)

    async def _aput(self: "BaseExternal", endpoint: str, **kwargs: t.Any) -> t.Any:
        return await self._arequest(method="PUT", endpoint=endpoint, **kwargs)

    async def _adelete(self: "BaseExternal", endpoint: str, **kwargs: t.Any) -> t.Any:
        return await self._arequest(method="DELETE", endpoint=endpoint, **kwargs)

    async def _apatch(self: "BaseExternal", endpoint: str, **kwargs: t.Any) -> t.Any:
        return await self._arequest(method="PATCH", endpoint=endpoint, **kwargs)

    async def _ahead(self: "BaseExternal", endpoint: str, **kwargs: t.Any) -> t.Any:
        return await self._arequest(method="HEAD", endpoint=endpoint, **kwargs)

    def _request(  # noqa: C901
        self: "BaseExternal",
        method: HttpMethod,
        endpoint: str,
        item: t.Union[str, int, None] = None,
        headers: t.Dict[str, str] = None,
        params: t.Dict[str, JsonValue[Primitives]] = None,
        data: t.Optional[t.Any] = None,
        timeout: t.Optional[int] = None,
        response_required: bool = False,
    ) -> t.Any:
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
                status = httpx.codes(response.status_code)
                error = self._parse_response(response)
                raise self._exception(
                    f'{status.name.replace("_", " ")}: {error}', level="danger"
                ) from None

        except httpx.HTTPError as http_err:
            raise self._exception(parse_exception(http_err), level="danger") from None

        return self._parse_response(response)

    def _get(self: "BaseExternal", endpoint: str, **kwargs: t.Any) -> t.Any:
        return self._request(method="GET", endpoint=endpoint, **kwargs)

    def _post(self: "BaseExternal", endpoint: str, **kwargs: t.Any) -> t.Any:
        return self._request(method="POST", endpoint=endpoint, **kwargs)

    def _put(self: "BaseExternal", endpoint: str, **kwargs: t.Any) -> t.Any:
        return self._request(method="PUT", endpoint=endpoint, **kwargs)

    def _delete(self: "BaseExternal", endpoint: str, **kwargs: t.Any) -> t.Any:
        return self._request(method="DELETE", endpoint=endpoint, **kwargs)

    def _patch(self: "BaseExternal", endpoint: str, **kwargs: t.Any) -> t.Any:
        return self._request(method="PATCH", endpoint=endpoint, **kwargs)

    def _head(self: "BaseExternal", endpoint: str, **kwargs: t.Any) -> t.Any:
        return self._request(method="HEAD", endpoint=endpoint, **kwargs)
