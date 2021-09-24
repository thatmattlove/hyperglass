"""Model utilities."""

# Standard Library
from typing import Any, Dict, Tuple

# Third Party
from pydantic import BaseModel

# Project
from hyperglass.log import log


class LegacyField(BaseModel):
    """Define legacy fields on a per-model basis.

    When `overwrite` is `True`, the old key is replaced with the new
    key. This will generally only occur when the value type is the same,
    and the key name has only changed names for clarity or cosmetic
    purposes.

    When `overwrite` is `False` and the old key is found, an error is
    raised. This generally occurs when the overall function of the old
    and new keys has remained the same, but the value type has changed,
    requiring the user to make changes to the config file.

    When `required` is `True` and neither the old or new keys are found,
    an error is raised. When `required` is false and neither keys are
    found, nothing happens.
    """

    old: str
    new: str
    overwrite: bool = False
    required: bool = True


LEGACY_FIELDS: Dict[str, Tuple[LegacyField, ...]] = {
    "Device": (
        LegacyField(old="nos", new="platform", overwrite=True),
        LegacyField(old="network", new="group", overwrite=False, required=False),
    ),
    "Proxy": (LegacyField(old="nos", new="platform", overwrite=True),),
}


def check_legacy_fields(*, model: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Check for legacy fields prior to model initialization."""
    if model in LEGACY_FIELDS:
        for field in LEGACY_FIELDS[model]:
            legacy_value = data.pop(field.old, None)
            new_value = data.get(field.new)
            if legacy_value is not None and new_value is None:
                if field.overwrite:
                    log.warning(
                        (
                            "The {!r} field has been deprecated and will be removed in a future release. "
                            "Use the {!r} field moving forward."
                        ),
                        f"{model}.{field.old}",
                        field.new,
                    )
                    data[field.new] = legacy_value
                else:
                    raise ValueError(
                        (
                            "The {!r} field has been replaced with the {!r} field. "
                            "Please consult the documentation and/or changelog to determine the appropriate migration path."
                        ).format(f"{model}.{field.old}", field.new)
                    )
            elif legacy_value is None and new_value is None and field.required:
                raise ValueError(f"'{field.new}' is missing")
    return data
