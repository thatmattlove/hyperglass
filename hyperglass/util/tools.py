"""Collection of generalized functional tools."""

# Standard Library
import typing as t

# Project
from hyperglass.types import Series

DeepConvert = t.TypeVar("DeepConvert", bound=t.Dict[str, t.Any])


def run_coroutine_in_new_thread(coroutine: t.Coroutine) -> t.Any:
    """Run an async function in a separate thread and get the result."""
    # Standard Library
    import asyncio
    import threading

    class Resolver(threading.Thread):
        def __init__(self, coro: t.Coroutine) -> None:
            self.result: t.Any = None
            self.coro: t.Coroutine = coro
            super().__init__()

        def run(self):
            self.result = asyncio.run(self.coro())

    thread = Resolver(coroutine)
    thread.start()
    thread.join()
    return thread.result


def split_on_uppercase(s: str) -> t.List[str]:
    """Split characters by uppercase letters.

    From: https://stackoverflow.com/a/40382663
    """
    string_length = len(s)
    is_lower_around = lambda: s[i - 1].islower() or string_length > (i + 1) and s[i + 1].islower()

    start = 0
    parts = []
    for i in range(1, string_length):
        if s[i].isupper() and is_lower_around():
            parts.append(s[start:i])
            start = i
    parts.append(s[start:])

    return parts


def parse_exception(exc: BaseException) -> str:
    """Parse an exception and its direct cause."""

    if not isinstance(exc, BaseException):
        raise TypeError(f"'{repr(exc)}' is not an exception.")

    def get_exc_name(exc):
        return " ".join(split_on_uppercase(exc.__class__.__name__))

    def get_doc_summary(doc):
        return doc.strip().split("\n")[0].strip(".")

    name = get_exc_name(exc)
    parsed = []
    if exc.__doc__:
        detail = get_doc_summary(exc.__doc__)
        parsed.append(f"{name} ({detail})")
    else:
        parsed.append(name)

    if exc.__cause__:
        cause = get_exc_name(exc.__cause__)
        if exc.__cause__.__doc__:
            cause_detail = get_doc_summary(exc.__cause__.__doc__)
            parsed.append(f"{cause} ({cause_detail})")
        else:
            parsed.append(cause)
    return ", caused by ".join(parsed)


def repr_from_attrs(obj: object, attrs: Series[str], strip: t.Optional[str] = None) -> str:
    """Generate a `__repr__()` value from a specific set of attribute names.

    Useful for complex models/objects where `__repr__()` should only display specific fields.
    """
    # Check the object to ensure each attribute actually exists, and deduplicate
    attr_names = {a for a in attrs if hasattr(obj, a)}
    # Dict representation of attr name to obj value (e.g. `obj.attr`), if the value has a
    # `__repr__` method.
    attr_values = {
        f if strip is None else f.strip(strip): v  # noqa: IF100
        for f in attr_names
        if hasattr((v := getattr(obj, f)), "__repr__")
    }
    pairs = (f"{k}={v!r}" for k, v in sorted(attr_values.items()))
    return f"{obj.__class__.__name__}({', '.join(pairs)})"


def snake_to_camel(value: str) -> str:
    """Convert a string from snake_case to camelCase."""
    head, *body = value.split("_")
    humps = (hump.capitalize() for hump in body)
    return "".join((head.lower(), *humps))


def get_fmt_keys(template: str) -> t.List[str]:
    """Get a list of str.format keys.

    For example, string `"The value of {key} is {value}"` returns
    `["key", "value"]`.
    """
    # Standard Library
    import string

    keys = []
    for block in (b for b in string.Formatter.parse("", template) if isinstance(template, str)):
        key = block[1]
        if key:
            keys.append(key)
    return keys


def deep_convert_keys(_dict: t.Type[DeepConvert], predicate: t.Callable[[str], str]) -> DeepConvert:
    """Convert all dictionary keys and nested dictionary keys."""
    converted = {}

    def get_value(value: t.Any):
        if isinstance(value, t.Dict):
            return {predicate(k): get_value(v) for k, v in value.items()}
        if isinstance(value, t.List):
            return [get_value(v) for v in value]
        if isinstance(value, t.Tuple):
            return tuple(get_value(v) for v in value)
        return value

    for key, value in _dict.items():
        converted[predicate(key)] = get_value(value)

    return converted


def at_least(
    minimum: int,
    value: int,
) -> int:
    """Get a number value that is at least a specified minimum."""
    if value < minimum:
        return minimum
    return value


def compare_dicts(dict_a: t.Dict[t.Any, t.Any], dict_b: t.Dict[t.Any, t.Any]) -> bool:
    """Determine if two dictationaries are (mostly) equal."""
    if isinstance(dict_a, t.Dict) and isinstance(dict_b, t.Dict):
        dict_a_keys, dict_a_values = set(dict_a.keys()), set(dict_a.values())
        dict_b_keys, dict_b_values = set(dict_b.keys()), set(dict_b.values())
        return all((dict_a_keys == dict_b_keys, dict_a_values == dict_b_values))
    return False


def compare_lists(left: t.List[t.Any], right: t.List[t.Any], *, ignore: Series[t.Any] = ()) -> bool:
    """Determine if all items in left list exist in right list."""
    left_ignored = [i for i in left if i not in ignore]
    diff_ignored = [i for i in left if i in right and i not in ignore]
    return len(left_ignored) == len(diff_ignored)


def compare_init(obj_a: object, obj_b: object) -> bool:
    """Compare the `__init__` annoations of two objects."""

    def _check_obj(obj: object):
        """Ensure `__annotations__` exists on the `__init__` method."""
        if hasattr(obj, "__init__") and isinstance(getattr(obj, "__init__", None), t.Callable):
            if hasattr(obj.__init__, "__annotations__") and isinstance(
                getattr(obj.__init__, "__annotations__", None), t.Dict
            ):
                return True
        return False

    if all((_check_obj(obj_a), _check_obj(obj_b))):
        obj_a.__init__.__annotations__.pop("self", None)
        obj_b.__init__.__annotations__.pop("self", None)
        return compare_dicts(obj_a.__init__.__annotations__, obj_b.__init__.__annotations__)
    return False


def dict_to_kwargs(in_dict: t.Dict[str, t.Any]) -> str:
    """Format a dict as a string of key/value pairs."""
    items = []
    for key, value in in_dict.items():
        out_str = f"{key}={value!r}"
        items = [*items, out_str]
    return " ".join(items)
