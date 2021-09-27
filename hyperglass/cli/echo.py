"""Helper functions for CLI message printing."""
# Standard Library
import typing as t

# Project
from hyperglass.log import HyperglassConsole


class Echo:
    """Container for console-printing functions."""

    _console = HyperglassConsole

    def _fmt(self, message: t.Any, *args: t.Any, **kwargs: t.Any) -> t.Any:
        if isinstance(message, str):
            args = (f"[bold]{arg}[/bold]" for arg in args)
            kwargs = {k: f"[bold]{v}[/bold]" for k, v in kwargs.items()}
            return message.format(*args, **kwargs)
        return message

    def error(self, message: str, *args, **kwargs):
        """Print an error message."""
        return self._console.print(self._fmt(message, *args, **kwargs), style="error")

    def info(self, message: str, *args, **kwargs):
        """Print an informational message."""
        return self._console.print(self._fmt(message, *args, **kwargs), style="info")

    def warning(self, message: str, *args, **kwargs):
        """Print a warning message."""
        return self._console.print(self._fmt(message, *args, **kwargs), style="info")

    def success(self, message: str, *args, **kwargs):
        """Print a success message."""
        return self._console.print(self._fmt(message, *args, **kwargs), style="success")

    def plain(self, message: str, *args, **kwargs):
        """Print an unformatted message."""
        return self._console.print(self._fmt(message, *args, **kwargs))


echo = Echo()
