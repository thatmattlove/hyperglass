"""HTTP Client for plugin use."""

# Standard Library
import typing as t

# Project
from hyperglass.models.fields import JsonValue, Primitives

# Local
from ._base import BaseExternal


class HTTPClient(BaseExternal, name="HTTPClient"):
    """Wrapper around a standard HTTP Client."""

    def __init__(self: "HTTPClient", base_url: str, timeout: int = 10) -> None:
        """Create an HTTPClient instance."""
        super().__init__(base_url=base_url, timeout=timeout, parse=False)

    async def aget(
        self: "HTTPClient",
        endpoint: str,
        headers: t.Dict[str, str] = None,
        params: t.Dict[str, JsonValue[Primitives]] = None,
        data: t.Optional[t.Any] = None,
        timeout: t.Optional[int] = None,
    ) -> t.Any:
        """Perform an async HTTP GET request."""
        return await self._arequest(
            method="GET",
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout,
        )

    async def apost(
        self: "HTTPClient",
        endpoint: str,
        headers: t.Dict[str, str] = None,
        params: t.Dict[str, JsonValue[Primitives]] = None,
        data: t.Optional[t.Any] = None,
        timeout: t.Optional[int] = None,
    ) -> t.Any:
        """Perform an async HTTP POST request."""
        return await self._arequest(
            method="POST",
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout,
        )

    async def aput(
        self: "HTTPClient",
        endpoint: str,
        headers: t.Dict[str, str] = None,
        params: t.Dict[str, JsonValue[Primitives]] = None,
        data: t.Optional[t.Any] = None,
        timeout: t.Optional[int] = None,
    ) -> t.Any:
        """Perform an async HTTP PUT request."""
        return await self._arequest(
            method="PUT",
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout,
        )

    async def adelete(
        self: "HTTPClient",
        endpoint: str,
        headers: t.Dict[str, str] = None,
        params: t.Dict[str, JsonValue[Primitives]] = None,
        data: t.Optional[t.Any] = None,
        timeout: t.Optional[int] = None,
    ) -> t.Any:
        """Perform an async HTTP DELETE request."""
        return await self._arequest(
            method="DELETE",
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout,
        )

    async def apatch(
        self: "HTTPClient",
        endpoint: str,
        headers: t.Dict[str, str] = None,
        params: t.Dict[str, JsonValue[Primitives]] = None,
        data: t.Optional[t.Any] = None,
        timeout: t.Optional[int] = None,
    ) -> t.Any:
        """Perform an async HTTP PATCH request."""
        return await self._arequest(
            method="PATCH",
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout,
        )

    async def ahead(
        self: "HTTPClient",
        endpoint: str,
        headers: t.Dict[str, str] = None,
        params: t.Dict[str, JsonValue[Primitives]] = None,
        data: t.Optional[t.Any] = None,
        timeout: t.Optional[int] = None,
    ) -> t.Any:
        """Perform an async HTTP HEAD request."""
        return await self._arequest(
            method="HEAD",
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout,
        )

    def get(
        self: "HTTPClient",
        endpoint: str,
        headers: t.Dict[str, str] = None,
        params: t.Dict[str, JsonValue[Primitives]] = None,
        data: t.Optional[t.Any] = None,
        timeout: t.Optional[int] = None,
    ) -> t.Any:
        """Perform an HTTP GET request."""
        return self._request(
            method="GET",
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout,
        )

    def post(
        self: "HTTPClient",
        endpoint: str,
        headers: t.Dict[str, str] = None,
        params: t.Dict[str, JsonValue[Primitives]] = None,
        data: t.Optional[t.Any] = None,
        timeout: t.Optional[int] = None,
    ) -> t.Any:
        """Perform an HTTP POST request."""
        return self._request(
            method="POST",
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout,
        )

    def put(
        self: "HTTPClient",
        endpoint: str,
        headers: t.Dict[str, str] = None,
        params: t.Dict[str, JsonValue[Primitives]] = None,
        data: t.Optional[t.Any] = None,
        timeout: t.Optional[int] = None,
    ) -> t.Any:
        """Perform an HTTP PUT request."""
        return self._request(
            method="PUT",
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout,
        )

    def delete(
        self: "HTTPClient",
        endpoint: str,
        headers: t.Dict[str, str] = None,
        params: t.Dict[str, JsonValue[Primitives]] = None,
        data: t.Optional[t.Any] = None,
        timeout: t.Optional[int] = None,
    ) -> t.Any:
        """Perform an HTTP DELETE request."""
        return self._request(
            method="DELETE",
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout,
        )

    def patch(
        self: "HTTPClient",
        endpoint: str,
        headers: t.Dict[str, str] = None,
        params: t.Dict[str, JsonValue[Primitives]] = None,
        data: t.Optional[t.Any] = None,
        timeout: t.Optional[int] = None,
    ) -> t.Any:
        """Perform an HTTP PATCH request."""
        return self._request(
            method="PATCH",
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout,
        )

    def head(
        self: "HTTPClient",
        endpoint: str,
        headers: t.Dict[str, str] = None,
        params: t.Dict[str, JsonValue[Primitives]] = None,
        data: t.Optional[t.Any] = None,
        timeout: t.Optional[int] = None,
    ) -> t.Any:
        """Perform an HTTP HEAD request."""
        return self._request(
            method="HEAD",
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout,
        )
