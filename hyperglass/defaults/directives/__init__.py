"""Built-in hyperglass directives."""

# Standard Library
import pkgutil
import importlib
from pathlib import Path

# Project
from hyperglass.log import log
from hyperglass.models.directive import Directives


def init_builtin_directives() -> "Directives":
    """Find all directives and register them with global state manager."""
    directives_dir = Path(__file__).parent
    directives = ()
    for _, name, __ in pkgutil.iter_modules([directives_dir]):
        module = importlib.import_module(f"hyperglass.defaults.directives.{name}")

        if not all((hasattr(module, "__all__"), len(getattr(module, "__all__", ())) > 0)):
            # Warn if there is no __all__ export or if it is empty.
            log.warning("Module '{!s}' is missing an '__all__' export", module)

        exports = (getattr(module, p) for p in module.__all__ if hasattr(module, p))
        directives += (*exports,)
    return Directives(*directives)
