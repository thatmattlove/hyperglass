"""Model utilities."""

# Standard Library
from typing import Any, Dict, Tuple

# Project
from hyperglass.log import log

LEGACY_FIELDS: Dict[str, Tuple[Tuple[str, str], ...]] = {
    "Device": (("nos", "type"),),
    "Proxy": (("nos", "type"),),
}


def check_legacy_fields(model: str, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Check for legacy fields prior to model initialization."""
    if model in LEGACY_FIELDS:
        for legacy_key, new_key in LEGACY_FIELDS[model]:
            legacy_value = kwargs.pop(legacy_key, None)
            new_value = kwargs.get(new_key)
            if legacy_value is not None and new_value is None:
                log.warning(
                    "The {} field has been deprecated and will be removed in a future release. Use the '{}' field moving forward.",
                    f"{model}.{legacy_key}",
                    new_key,
                )
                kwargs[new_key] = legacy_value
            elif legacy_value is None and new_value is None:
                raise ValueError(f"'{new_key}' is missing")
    return kwargs
