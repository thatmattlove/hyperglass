"""Access hyperglass global system settings."""

# Standard Library
import typing as t

if t.TYPE_CHECKING:
    # Local
    from .models.system import HyperglassSystem


def _system_settings() -> "HyperglassSystem":
    """Get system settings from local environment."""
    # Local
    from .models.system import HyperglassSystem

    return HyperglassSystem()


Settings = _system_settings()
