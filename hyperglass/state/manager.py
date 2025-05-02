"""hyperglass global state."""

# Standard Library
import typing as t

# Third Party
from redis import Redis, ConnectionPool

# Project
from hyperglass.util import repr_from_attrs

# Local
from .redis import RedisManager

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.system import HyperglassSettings


class StateManager:
    """Global State Manager.

    Maintains configuration objects in Redis cache and accesses them as needed.
    """

    settings: "HyperglassSettings"
    redis: RedisManager
    _namespace: str = "hyperglass.state"

    def __init__(self, *, settings: "HyperglassSettings") -> None:
        """Set up Redis connection and add configuration objects."""

        self.settings = settings
        connection_pool = ConnectionPool.from_url(**self.settings.redis_connection_pool)
        redis = Redis(connection_pool=connection_pool)
        self.redis = RedisManager(instance=redis, namespace=self._namespace)

    def __repr__(self) -> str:
        """Represent state manager by name and namespace."""
        return repr_from_attrs(self, ("redis", "namespace"))

    def __str__(self) -> str:
        """Represent state manager by __repr__."""
        return repr(self)

    @classmethod
    def properties(cls: "StateManager") -> t.Tuple[str, ...]:
        """Get all read-only properties of the state manager."""
        return tuple(
            attr
            for attr in dir(cls)
            if not attr.startswith("_") and "fget" in dir(getattr(cls, attr))
        )
