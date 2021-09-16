"""Interact with redis for state management."""

# Standard Library
import pickle
import typing as t
from typing import overload
from datetime import datetime, timedelta

# Project
from hyperglass.exceptions.private import StateError

if t.TYPE_CHECKING:
    # Third Party
    from redis import Redis


class RedisManager:
    """Convenience wrapper for managing a redis session."""

    instance: "Redis"
    namespace: str

    def __init__(self, instance: "Redis", namespace: str) -> None:
        """Set up Redis connection and add configuration objects."""
        self.instance = instance
        self.namespace = namespace

    def __repr__(self) -> str:
        """Alias repr to Redis instance's repr."""
        return repr(self.instance)

    def __str__(self) -> str:
        """String-friendly redis manager."""
        return repr(self)

    def _key_join(self, *keys: str) -> str:
        """Format keys with state namespace."""
        key_in_parts = (k for key in keys for k in key.split("."))
        key_parts = list(dict.fromkeys((*self.namespace.split("."), *key_in_parts)))
        return ".".join(key_parts)

    def key(self, key: t.Union[str, t.Sequence[str]]) -> str:
        """Format keys with state namespace."""
        if isinstance(key, (t.List, t.Tuple, t.Generator)):
            return self._key_join(*key)
        return self._key_join(key)

    def check(self) -> bool:
        """Ensure the redis instance is running and reachable."""
        result = self.instance.ping()
        if result is False:
            raise RuntimeError(
                "Redis instance {!r} is not running or reachable".format(self.instance)
            )
        return result

    def delete(self, key: t.Union[str, t.Sequence[str]]) -> None:
        """Delete a key and value from the cache."""
        self.instance.delete(self.key(key))

    def expire(
        self,
        key: t.Union[str, t.Sequence[str]],
        *,
        expire_in: t.Optional[t.Union[timedelta, int]] = None,
        expire_at: t.Optional[t.Union[datetime, int]] = None,
    ) -> None:
        """Expire a cache key, either at a time, or in a number of seconds.

        If no at or in time is specified, the key is deleted.
        """
        key = self.key(key)
        if isinstance(expire_at, (datetime, int)):
            self.instance.expireat(key, expire_at)
            return
        if isinstance(expire_in, (timedelta, int)):
            self.instance.expire(key, expire_in)
            return
        self.instance.delete(key)

    def get(
        self,
        key: t.Union[str, t.Sequence[str]],
        *,
        raise_if_none: bool = False,
        value_if_none: t.Any = None,
    ) -> t.Union[None, t.Any]:
        """Get and decode a value from the cache."""
        name = self.key(key)
        value: t.Optional[bytes] = self.instance.get(name)
        if isinstance(value, bytes):
            return pickle.loads(value)
        if raise_if_none is True:
            raise StateError("'{key}' ('{name}') does not exist in Redis store", key=key, name=name)
        if value_if_none is not None:
            return value_if_none
        return None

    def set(self, key: t.Union[str, t.Sequence[str]], value: t.Any) -> None:
        """Add an object to the cache."""
        name = self.key(key)
        self.instance.set(name, pickle.dumps(value))

    @overload
    def get_map(self, key: str, item: str) -> t.Any:
        """Get a single value from a Redis hash map (dict)."""

    @overload
    def get_map(self, key: str, item=None) -> t.Any:
        """Get a single value from a Redis hash map (dict)."""

    def get_map(self, key: str, item: t.Optional[str] = None) -> t.Any:
        """Get a Redis hash map or hash map value."""
        name = self.key(key)
        if isinstance(item, str):
            value = self.instance.hget(name, item)
        else:
            value = self.instance.hgetall(name)

        if isinstance(value, bytes):
            return pickle.loads(value)
        return None

    def set_map_item(self, key: str, item: str, value: t.Any) -> None:
        """Add a value to a hash map (dict)."""
        name = self.key(key)
        self.instance.hset(name, item, pickle.dumps(value))
