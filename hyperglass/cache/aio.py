"""Asyncio Redis cache handler."""

# Standard Library
import json
import time
import pickle
import typing as t
import asyncio

# Third Party
from aredis import StrictRedis as AsyncRedis  # type: ignore
from pydantic import SecretStr
from aredis.exceptions import RedisError  # type: ignore

# Project
from hyperglass.cache.base import BaseCache
from hyperglass.exceptions.private import DependencyError

if t.TYPE_CHECKING:
    # Third Party
    from aredis.pubsub import PubSub as AsyncPubSub  # type: ignore

    # Project
    from hyperglass.models.config.params import Params
    from hyperglass.models.config.devices import Devices


class AsyncCache(BaseCache):
    """Asynchronous Redis cache handler."""

    def __init__(
        self,
        *,
        db: int,
        host: str = "localhost",
        port: int = 6379,
        password: t.Optional[SecretStr] = None,
        decode_responses: bool = False,
        **kwargs: t.Any,
    ):
        """Initialize Redis connection."""
        super().__init__(
            db=db,
            host=host,
            port=port,
            password=password,
            decode_responses=decode_responses,
            **kwargs,
        )

        password = self.password
        if password is not None:
            password = password.get_secret_value()

        self.instance: AsyncRedis = AsyncRedis(
            db=self.db,
            host=self.host,
            port=self.port,
            password=password,
            decode_responses=self.decode_responses,
            **self.redis_args,
        )

    async def test(self):
        """Send an echo to Redis to ensure it can be reached."""
        try:
            await self.instance.echo("hyperglass test")
        except RedisError as err:
            err_msg = str(err)
            if not err_msg and hasattr(err, "__context__"):
                # Some Redis exceptions are raised without a message
                # even if they are raised from another exception that
                # does have a message.
                err_msg = str(err.__context__)

            if "auth" in err_msg.lower():
                raise DependencyError(
                    "Authentication to Redis server {s} failed with message: '{e}'",
                    s=repr(self, e=err_msg),
                )

            else:
                raise DependencyError(
                    "Unable to connect to Redis server {s} due to error {e}",
                    s=repr(self),
                    e=err_msg,
                )

    async def get(self, *args: str) -> t.Any:
        """Get item(s) from cache."""
        if len(args) == 1:
            raw = await self.instance.get(args[0])
        else:
            raw = await self.instance.mget(args)
        return self.parse_types(raw)

    async def get_dict(self, key: str, field: str = "") -> t.Any:
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

        if isinstance(value, t.Dict):
            value = json.dumps(value)
        else:
            value = str(value)

        response = await self.instance.hset(key, field, value)

        if response in (0, 1):
            success = True

        return success

    async def wait(self, pubsub: "AsyncPubSub", timeout: int = 30, **kwargs) -> t.Any:
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

    async def pubsub(self) -> "AsyncPubSub":
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

    async def get_params(self: "AsyncCache") -> "Params":
        """Get Params object from the cache."""
        params = await self.instance.get(self.CONFIG_KEY)
        return pickle.loads(params)

    async def get_devices(self: "AsyncCache") -> "Devices":
        """Get Devices object from the cache."""
        devices = await self.instance.get(self.DEVICES_KEY)
        return pickle.loads(devices)

    async def set_config(self: "AsyncCache", config: "Params") -> None:
        """Add a params instance to the cache."""
        await self.instance.set(self.CONFIG_KEY, pickle.dumps(config))

    async def set_devices(self: "AsyncCache", devices: "Devices") -> None:
        """Add a devices instance to the cache."""
        await self.instance.set(self.DEVICES_KEY, pickle.dumps(devices))
