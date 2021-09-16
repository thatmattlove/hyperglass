"""API Events."""

# Project
from hyperglass.state import use_state


def check_redis() -> None:
    """Ensure Redis is running before starting server."""
    cache = use_state("cache")
    cache.check()


on_startup = (check_redis,)
on_shutdown = ()
