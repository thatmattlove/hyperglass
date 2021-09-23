"""Access hyperglass global system settings."""

# Standard Library
import typing as t

if t.TYPE_CHECKING:
    # Local
    from .models.system import HyperglassSettings


def _system_settings() -> "HyperglassSettings":
    """Get system settings from local environment."""
    # Local
    from .models.system import HyperglassSettings

    return HyperglassSettings()


Settings = _system_settings()
