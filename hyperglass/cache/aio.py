"""Asyncio Redis cache handler."""

# Standard Library
import json
import time
import pickle
import asyncio
from typing import Any, Dict

# Third Party
from aredis import StrictRedis as AsyncRedis
from aredis.pubsub import PubSub as AsyncPubSub

# Project
from hyperglass.cache.base import BaseCache


class AsyncCache(BaseCache):
    """Asynchronous Redis cache handler."""

    def __init__(self, *args, **kwargs):
        """Initialize Redis connection."""
        super().__init__(*args, **kwargs)
        self.instance: AsyncRedis = AsyncRedis(
            db=self.db,
            host=self.host,
            port=self.port,
            decode_responses=self.decode_responses,
            **self.redis_args,
        )

    async def get(self, *args: str) -> Any:
        """Get item(s) from cache."""
        if len(args) == 1:
            raw = await self.instance.get(args[0])
        else:
            raw = await self.instance.mget(args)
        return self.parse_types(raw)

    async def get_dict(self, key: str, field: str = "") -> Any:
        """Get hash map (dict) item(s)."""
        if not field:
            raw = await self.instance.hgetall(key)
        else:
            raw = await self.instance.hget(key, field)

        return self.parse_types(raw)

    async def set(self, key: str, value: str) -> bool:
        """Set cache values."""
        return await self.instance.set(key, value)

    async def set_dict(self, key: str, field: str, value: str) -> bool:
        """Set hash map (dict) values."""
        success = False

        if isinstance(value, Dict):
            value = json.dumps(value)
        else:
            value = str(value)

        response = await self.instance.hset(key, field, value)

        if response in (0, 1):
            success = True

        return success

    async def wait(self, pubsub: AsyncPubSub, timeout: int = 30, **kwargs) -> Any:
        """Wait for pub/sub messages & return posted message."""
        now = time.time()
        timeout = now + timeout

        while now < timeout:

            message = await pubsub.get_message(ignore_subscribe_messages=True, **kwargs)

            if message is not None and message["type"] == "message":
                data = message["data"]
                return self.parse_types(data)

            await asyncio.sleep(0.01)
            now = time.time()

        return None

    async def pubsub(self) -> AsyncPubSub:
        """Provide an aredis.pubsub.Pubsub instance."""
        return self.instance.pubsub()

    async def pub(self, key: str, value: str) -> None:
        """Publish a value."""
        await asyncio.sleep(1)
        await self.instance.publish(key, value)

    async def clear(self) -> None:
        """Clear the cache."""
        await self.instance.flushdb()

    async def delete(self, *keys: str) -> None:
        """Delete a cache key."""
        await self.instance.delete(*keys)

    async def expire(self, *keys: str, seconds: int) -> None:
        """Set timeout of key in seconds."""
        for key in keys:
            await self.instance.expire(key, seconds)

    async def get_config(self) -> Dict:
        """Get picked config object from cache."""

        pickled = await self.instance.get("HYPERGLASS_CONFIG")
        return pickle.loads(pickled)
