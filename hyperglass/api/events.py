"""API Events."""

# Project
from hyperglass.state import use_state


def check_redis() -> bool:
    """Ensure Redis is running before starting server."""
    state = use_state()
    return state.redis.ping()


on_startup = (check_redis,)
on_shutdown = ()
