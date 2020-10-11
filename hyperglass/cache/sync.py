"""Non-asyncio Redis cache handler."""

# Standard Library
import json
import time
import pickle
from typing import Any, Dict

# Third Party
from redis import Redis as SyncRedis
from redis.client import PubSub as SyncPubsSub
from redis.exceptions import RedisError

# Project
from hyperglass.cache.base import BaseCache
from hyperglass.exceptions import HyperglassError


class SyncCache(BaseCache):
    """Synchronous Redis cache handler."""

    def __init__(self, *args, **kwargs):
        """Initialize Redis connection."""
        super().__init__(*args, **kwargs)

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
                raise HyperglassError(
                    "Authentication to Redis server {server} failed.".format(
                        server=repr(self)
                    ),
                    level="danger",
                ) from None
            else:
                raise HyperglassError(
                    "Unable to connect to Redis server {server}".format(
                        server=repr(self)
                    ),
                    level="danger",
                ) from None

    def get(self, *args: str) -> Any:
        """Get item(s) from cache."""
        if len(args) == 1:
            raw = self.instance.get(args[0])
        else:
            raw = self.instance.mget(args)
        return self.parse_types(raw)

    def get_dict(self, key: str, field: str = "") -> Any:
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

        if isinstance(value, Dict):
            value = json.dumps(value)
        else:
            value = str(value)

        response = self.instance.hset(key, str(field), value)

        if response in (0, 1):
            success = True

        return success

    def wait(self, pubsub: SyncPubsSub, timeout: int = 30, **kwargs) -> Any:
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

    def pubsub(self) -> SyncPubsSub:
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

    def get_config(self) -> Dict:
        """Get picked config object from cache."""

        pickled = self.instance.get("HYPERGLASS_CONFIG")
        return pickle.loads(pickled)
