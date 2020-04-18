"""Redis cache handler."""

# Standard Library
import time
import asyncio

# Third Party
from aredis import StrictRedis


class Cache:
    """Redis cache handler."""

    def __init__(
        self, db, host="localhost", port=6379, decode_responses=True, **kwargs
    ):
        """Initialize Redis connection."""
        self.db: int = db
        self.host: str = host
        self.port: int = port
        self.instance: StrictRedis = StrictRedis(
            db=self.db,
            host=self.host,
            port=self.port,
            decode_responses=decode_responses,
            **kwargs,
        )

    def __repr__(self):
        """Represent class state."""
        return f"ConfigCache(db={self.db}, host={self.host}, port={self.port})"

    def __getitem__(self, item):
        """Enable subscriptable syntax."""
        return self.get(item)

    @staticmethod
    async def _parse_types(value):
        """Parse a string to standard python types."""
        import re

        async def _parse_string(str_value):

            is_float = (re.compile(r"^(\d+\.\d+)$"), float)
            is_int = (re.compile(r"^(\d+)$"), int)
            is_bool = (re.compile(r"^(True|true|False|false)$"), bool)
            is_none = (re.compile(r"^(None|none|null|nil|\(nil\))$"), lambda v: None)

            for pattern, factory in (is_float, is_int, is_bool, is_none):
                if isinstance(str_value, str) and bool(re.match(pattern, str_value)):
                    str_value = factory(str_value)
                    break
            return str_value

        if isinstance(value, str):
            value = await _parse_string(value)
        elif isinstance(value, bytes):
            value = await _parse_string(value.decode("utf-8"))
        elif isinstance(value, list):
            value = [await _parse_string(i) for i in value]
        elif isinstance(value, tuple):
            value = tuple(await _parse_string(i) for i in value)

        return value

    async def get(self, *args):
        """Get item(s) from cache."""
        if len(args) == 1:
            raw = await self.instance.get(args[0])
        else:
            raw = await self.instance.mget(args)
        return await self._parse_types(raw)

    async def get_dict(self, key, field=None):
        """Get hash map (dict) item(s)."""
        if field is None:
            raw = await self.instance.hgetall(key)
        else:
            raw = await self.instance.hget(key, field)
        return await self._parse_types(raw)

    async def set(self, key, value):
        """Set cache values."""
        return await self.instance.set(key, value)

    async def set_dict(self, key, field, value):
        """Set hash map (dict) values."""
        return await self.instance.hset(key, field, value)

    async def wait(self, pubsub, timeout=30, **kwargs):
        """Wait for pub/sub messages & return posted message."""
        now = time.time()
        timeout = now + timeout
        while now < timeout:
            message = await pubsub.get_message(ignore_subscribe_messages=True, **kwargs)
            if message is not None and message["type"] == "message":
                data = message["data"]
                return await self._parse_types(data)

            await asyncio.sleep(0.01)
            now = time.time()
        return None

    async def pubsub(self):
        """Provide an aredis.pubsub.Pubsub instance."""
        return self.instance.pubsub()

    async def pub(self, key, value):
        """Publish a value."""
        await asyncio.sleep(1)
        await self.instance.publish(key, value)

    async def clear(self):
        """Clear the cache."""
        await self.instance.flushdb()

    async def delete(self, *keys):
        """Delete a cache key."""
        await self.instance.delete(*keys)

    async def expire(self, *keys, seconds):
        """Set timeout of key in seconds."""
        for key in keys:
            await self.instance.expire(key, seconds)

    async def aget_config(self):
        """Get picked config object from cache."""
        import pickle

        pickled = await self.instance.get("HYPERGLASS_CONFIG")
        return pickle.loads(pickled)

    def get_config(self):
        """Get picked config object from cache."""
        import pickle
        from hyperglass.compat._asyncio import aiorun

        pickled = aiorun(self.instance.get("HYPERGLASS_CONFIG"))
        return pickle.loads(pickled)
