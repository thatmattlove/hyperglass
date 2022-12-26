"""Functions for maintaining compatibility with older Python versions or libraries."""

# Local
from ._sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError, open_tunnel

__all__ = (
    "BaseSSHTunnelForwarderError",
    "open_tunnel",
    "SSHTunnelForwarder",
)
