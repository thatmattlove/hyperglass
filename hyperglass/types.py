"""Custom types."""

# Standard Library
import typing as _t

_S = _t.TypeVar("_S")

Series = _t.Union[_t.MutableSequence[_S], _t.Tuple[_S], _t.Set[_S]]
"""Like `typing.Sequence`, but excludes `str`."""
