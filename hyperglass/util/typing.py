"""Typing utilities."""

# Standard Library
import typing
import inspect


def is_type(value: typing.Any, *types: typing.Any) -> bool:
    """Verify if the type of `value` matches any provided type in `types`.

    Will only check the main type for generics like `Dict` or `List`, but will check the individual
    types of generics like `Union` or `Optional`.

    Probably wrong, but seems to work for most cases.
    """
    for _type in types:
        if _type is None:
            return value is None
        if inspect.isclass(_type):
            return isinstance(value, _type)
        origin = typing.get_origin(_type)
        if origin is typing.Union:
            return any(is_type(value, t) for t in _type.__args__)
        if origin is None:
            return isinstance(value, type(_type))
        return isinstance(value, origin)
    return False


def is_series(value: typing.Any) -> bool:
    """Determine if a value is a `hyperglass.types.Series`, i.e. non-string `typing.Sequence`."""
    if isinstance(value, (typing.MutableSequence, typing.Tuple, typing.Set)):
        return True
    return False
