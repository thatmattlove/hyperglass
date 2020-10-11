"""Base Redis cache handler."""

# Standard Library
import re
import json
from typing import Any, Optional

# Third Party
from pydantic import SecretStr


class BaseCache:
    """Redis cache handler."""

    def __init__(
        self,
        db: int,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[SecretStr] = None,
        decode_responses: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize Redis connection."""
        self.db: int = db
        self.host: str = str(host)
        self.port: int = port
        self.password: Optional[SecretStr] = password
        self.decode_responses: bool = decode_responses
        self.redis_args: dict = kwargs

    def __repr__(self) -> str:
        """Represent class state."""
        return "HyperglassCache(db={}, host={}, port={}, password={})".format(
            self.db, self.host, self.port, self.password
        )

    def parse_types(self, value: str) -> Any:
        """Parse a string to standard python types."""

        def parse_string(str_value: str):

            is_float = (re.compile(r"^(\d+\.\d+)$"), float)
            is_int = (re.compile(r"^(\d+)$"), int)
            is_bool = (re.compile(r"^(True|true|False|false)$"), bool)
            is_none = (re.compile(r"^(None|none|null|nil|\(nil\))$"), lambda v: None)
            is_jsonable = (re.compile(r"^[\{\[].*[\}\]]$"), json.loads)

            for pattern, factory in (is_float, is_int, is_bool, is_none, is_jsonable):
                if isinstance(str_value, str) and bool(re.match(pattern, str_value)):
                    str_value = factory(str_value)
                    break
            return str_value

        if isinstance(value, str):
            value = parse_string(value)
        elif isinstance(value, bytes):
            value = parse_string(value.decode("utf-8"))
        elif isinstance(value, list):
            value = [parse_string(i) for i in value]
        elif isinstance(value, tuple):
            value = tuple(parse_string(i) for i in value)
        elif isinstance(value, dict):
            value = {k: self.parse_types(v) for k, v in value.items()}

        return value
