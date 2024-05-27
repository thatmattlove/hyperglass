"""hyperglass System Settings model."""

# Standard Library
import typing as t
from pathlib import Path
from ipaddress import ip_address

# Third Party
from pydantic import (
    FilePath,
    RedisDsn,
    SecretStr,
    DirectoryPath,
    IPvAnyAddress,
    ValidationInfo,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project
from hyperglass.util import at_least, cpu_count

if t.TYPE_CHECKING:
    # Third Party
    from rich.console import Console, RenderResult, ConsoleOptions

ListenHost = t.Union[None, IPvAnyAddress, t.Literal["localhost"]]

_default_app_path = Path("/etc/hyperglass")


class HyperglassSettings(BaseSettings):
    """hyperglass system settings, required to start hyperglass."""

    model_config = SettingsConfigDict(env_prefix="hyperglass_")

    config_file_names: t.ClassVar[t.Tuple[str, ...]] = ("config", "devices", "directives")
    default_app_path: t.ClassVar[Path] = _default_app_path
    original_app_path: Path = _default_app_path

    debug: bool = False
    dev_mode: bool = False
    disable_ui: bool = False
    app_path: DirectoryPath = _default_app_path
    redis_host: str = "localhost"
    redis_password: t.Optional[SecretStr] = None
    redis_db: int = 1
    redis_dsn: RedisDsn = None
    host: IPvAnyAddress = None
    port: int = 8001
    ca_cert: t.Optional[FilePath] = None
    container: bool = False

    def __init__(self, **kwargs) -> None:
        """Create hyperglass Settings instance."""
        super().__init__(**kwargs)
        if self.container:
            self.app_path = self.default_app_path

    def __rich_console__(self, console: "Console", options: "ConsoleOptions") -> "RenderResult":
        """Render a Rich table representation of hyperglass settings."""
        # Third Party
        from rich.panel import Panel
        from rich.style import Style
        from rich.table import Table, box
        from rich.pretty import Pretty

        table = Table(box=box.MINIMAL, border_style="subtle")
        table.add_column("Environment Variable", style=Style(color="#118ab2", bold=True))
        table.add_column("Value")
        params = sorted(
            (
                "debug",
                "dev_mode",
                "app_path",
                "redis_host",
                "redis_db",
                "redis_dsn",
                "host",
                "port",
            )
        )
        for attr in params:
            table.add_row(f"hyperglass_{attr}".upper(), Pretty(getattr(self, attr)))

        yield Panel.fit(table, title="hyperglass settings", border_style="subtle")

    @field_validator("host", mode="before")
    def validate_host(
        cls: "HyperglassSettings", value: t.Any, info: ValidationInfo
    ) -> IPvAnyAddress:
        """Set default host based on debug mode."""

        if value is None:
            if info.data.get("debug") is False:
                return ip_address("::1")
            if info.data.get("debug") is True:
                return ip_address("::")

        if isinstance(value, str):
            if value != "localhost":
                try:
                    return ip_address(value)
                except ValueError as err:
                    raise ValueError(str(value)) from err

            elif value == "localhost":
                return ip_address("::1")

        raise ValueError(str(value))

    @field_validator("redis_dsn", mode="before")
    def validate_redis_dsn(cls, value: t.Any, info: ValidationInfo) -> RedisDsn:
        """Construct a Redis DSN if none is provided."""
        if value is None:
            host = info.data.get("redis_host")
            db = info.data.get("redis_db")
            dsn = "redis://{}/{!s}".format(host, db)
            password = info.data.get("redis_password")
            if password is not None:
                dsn = "redis://:{}@{}/{!s}".format(password.get_secret_value(), host, db)
            return dsn
        return value

    def bind(self: "HyperglassSettings") -> str:
        """Format a listen_address. Wraps IPv6 address in brackets."""
        if self.host.version == 6:
            return f"[{self.host!s}]:{self.port!s}"
        return f"{self.host!s}:{self.port!s}"

    @property
    def log_level(self: "HyperglassSettings") -> str:
        """Get log level as string, inferred from debug mode."""
        if self.debug:
            return "DEBUG"
        return "WARNING"

    @property
    def workers(self: "HyperglassSettings") -> int:
        """Get worker count, inferred from debug mode."""
        if self.debug:
            return 1
        return cpu_count(2)

    @property
    def redis(self: "HyperglassSettings") -> t.Dict[str, t.Union[None, int, str]]:
        """Get redis parameters as a dict for convenient connection setups."""
        password = None
        if self.redis_password is not None:
            password = self.redis_password.get_secret_value()

        return {
            "db": self.redis_db,
            "host": self.redis_host,
            "password": password,
        }

    @property
    def redis_connection_pool(self: "HyperglassSettings") -> t.Dict[str, t.Any]:
        """Get Redis ConnectionPool keyword arguments."""
        return {"url": str(self.redis_dsn), "max_connections": at_least(8, cpu_count(2))}

    @property
    def dev_url(self: "HyperglassSettings") -> str:
        """Get the hyperglass URL for when dev_mode is enabled."""
        return f"http://localhost:{self.port!s}/"

    @property
    def prod_url(self: "HyperglassSettings") -> str:
        """Get the UI-facing hyperglass URL/path."""
        return "/api/"

    @property
    def static_path(self: "HyperglassSettings") -> Path:
        """Get static asset path."""
        return Path(self.app_path / "static")
