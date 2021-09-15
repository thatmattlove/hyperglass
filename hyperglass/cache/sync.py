"""Non-asyncio Redis cache handler."""

# Standard Library
import json
import time
import pickle
import typing as t

# Third Party
from redis import Redis as SyncRedis
from pydantic import SecretStr
from redis.exceptions import RedisError

# Project
from hyperglass.cache.base import BaseCache
from hyperglass.exceptions.private import DependencyError

if t.TYPE_CHECKING:
    # Third Party
    from redis.client import PubSub as SyncPubsSub

    # Project
    from hyperglass.models.config.params import Params
    from hyperglass.models.config.devices import Devices


class SyncCache(BaseCache):
    """Synchronous Redis cache handler."""

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

        self.instance: SyncRedis = SyncRedis(
            db=self.db,
            host=self.host,
            port=self.port,
            password=password,
            decode_responses=self.decode_responses,
            **self.redis_args,
        )

    def test(self):
        """Send an echo to Redis to ensure it can be reached."""
        try:
            self.instance.echo("hyperglass test")
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

    def get(self, *args: str, decode: bool = True) -> t.Any:
        """Get item(s) from cache."""
        if len(args) == 1:
            raw = self.instance.get(args[0])
        else:
            raw = self.instance.mget(args)
        if decode and isinstance(raw, bytes):
            raw = raw.decode()

        return self.parse_types(raw)

    GetObj = t.TypeVar("GetObj")

    def get_object(self, name: str, _type: t.Type[GetObj] = t.Any) -> GetObj:
        raw = self.instance.get(name)
        obj: _type = pickle.loads(raw)
        return obj

    def get_dict(self, key: str, field: str = "", *, decode: bool = True) -> t.Any:
        """Get hash map (dict) item(s)."""
        if not field:
            raw = self.instance.hgetall(key)
        else:
            raw = self.instance.hget(key, str(field))

        return self.parse_types(raw)

    def set(self, key: str, value: str) -> bool:
        """Set cache values."""
        return self.instance.set(key, str(value))

    def set_dict(self, key: str, field: str, value: str) -> bool:
        """Set hash map (dict) values."""
        success = False

        if isinstance(value, t.Dict):
            value = json.dumps(value)
        else:
            value = str(value)

        response = self.instance.hset(key, str(field), value)

        if response in (0, 1):
            success = True

        return success

    def wait(self, pubsub: "SyncPubsSub", timeout: int = 30, **kwargs) -> t.Any:
        """Wait for pub/sub messages & return posted message."""
        now = time.time()
        timeout = now + timeout

        while now < timeout:

            message = pubsub.get_message(ignore_subscribe_messages=True, **kwargs)

            if message is not None and message["type"] == "message":
                data = message["data"]
                return self.parse_types(data)

            time.sleep(0.01)
            now = time.time()

        return None

    def pubsub(self) -> "SyncPubsSub":
        """Provide a redis.client.Pubsub instance."""
        return self.instance.pubsub()

    def pub(self, key: str, value: str) -> None:
        """Publish a value."""
        time.sleep(1)
        self.instance.publish(key, value)

    def clear(self) -> None:
        """Clear the cache."""
        self.instance.flushdb()

    def delete(self, *keys: str) -> None:
        """Delete a cache key."""
        self.instance.delete(*keys)

    def expire(self, *keys: str, seconds: int) -> None:
        """Set timeout of key in seconds."""
        for key in keys:
            self.instance.expire(key, seconds)

    def get_params(self) -> "Params":
        """Get Params object from the cache."""
        return self.get_object(self.CONFIG_KEY, "Params")
        # return pickle.loads(self.get(self.CONFIG_KEY, decode=False, parse=False))

    def get_devices(self) -> "Devices":
        """Get Devices object from the cache."""
        return self.get_object(self.DEVICES_KEY, "Devices")
        # return pickle.loads(self.get(self.DEVICES_KEY, decode=False, parse=False))

    def set_config(self: "SyncCache", config: "Params") -> None:
        """Add a params instance to the cache."""
        self.instance.set(self.CONFIG_KEY, pickle.dumps(config))

    def set_devices(self: "SyncCache", devices: "Devices") -> None:
        """Add a devices instance to the cache."""
        self.instance.set(self.DEVICES_KEY, pickle.dumps(devices))
