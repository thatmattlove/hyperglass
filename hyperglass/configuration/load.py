"""Collect configurations from files."""

# Standard Library
import typing as t
from pathlib import Path

# Project
from hyperglass.log import log
from hyperglass.util import run_coroutine_in_new_thread
from hyperglass.settings import Settings
from hyperglass.constants import CONFIG_EXTENSIONS
from hyperglass.exceptions.private import ConfigError, ConfigMissing, ConfigLoaderMissing

LoadedConfig = t.Union[t.Dict[str, t.Any], t.List[t.Any], t.Tuple[t.Any, ...]]


def find_path(file_name: str, *, required: bool) -> t.Union[Path, None]:
    """Find the first matching configuration file."""
    for extension in CONFIG_EXTENSIONS:
        path = Settings.app_path / f"{file_name}.{extension}"
        if path.exists():
            return path

    if required:
        raise ConfigMissing(file_name, app_path=Settings.app_path)
    return None


def load_dsl(path: Path, *, empty_allowed: bool) -> LoadedConfig:
    """Verify and load data from DSL (non-python) config files."""
    loader = None
    if path.suffix in (".yaml", ".yml"):
        try:
            # Third Party
            import yaml

            loader = yaml.safe_load

        except ImportError as err:
            raise ConfigLoaderMissing(path) from err
    elif path.suffix == ".toml":
        try:
            # Third Party
            import toml

            loader = toml.load

        except ImportError as err:
            raise ConfigLoaderMissing(path) from err

    elif path.suffix == ".json":
        # Standard Library
        import json

        loader = json.load

    if loader is None:
        raise ConfigLoaderMissing(path)

    with path.open("r") as f:
        data = loader(f)
        if data is None and empty_allowed is False:
            raise ConfigError(
                "'{!s}' exists, but it is empty and is required to start hyperglass.".format(path),
            )
    log.bind(path=path).debug("Loaded configuration")
    return data or {}


def load_python(path: Path, *, empty_allowed: bool) -> LoadedConfig:
    """Import configuration from a python configuration file."""
    # Standard Library
    import inspect
    from importlib.util import module_from_spec, spec_from_file_location

    # Load the file as a module.
    name, _ = path.name.split(".")
    spec = spec_from_file_location(name, location=path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    # Get all exports that are named 'main' (any case).
    exports = tuple(getattr(module, e, None) for e in dir(module) if e.lower() == "main")
    if len(exports) < 1:
        # Raise an error if there are no exports named main.
        raise ConfigError(
            f"'{path!s} exists', but it is missing a variable or function named 'main'"
        )
    # Pick the first export named main.
    main, *_ = exports
    data = None
    if isinstance(main, t.Callable):
        if inspect.iscoroutinefunction(main):
            # Resolve an async funcion.
            data = run_coroutine_in_new_thread(main)
        else:
            # Resolve a standard function.
            data = main()
    elif isinstance(main, (t.Dict, t.List, t.Tuple)):
        data = main

    if data is None and empty_allowed is False:
        raise ConfigError(f"'{path!s} exists', but variable or function 'main' is an invalid type")

    log.bind(path=path).debug("Loaded configuration")
    return data or {}


def load_config(name: str, *, required: bool) -> LoadedConfig:
    """Load a configuration file."""
    path = find_path(name, required=required)

    if path is None and required is False:
        return {}

    if path.suffix == ".py":
        return load_python(path, empty_allowed=not required)

    if path.suffix.replace(".", "") in CONFIG_EXTENSIONS:
        return load_dsl(path, empty_allowed=not required)

    raise ConfigError(
        "{p} has an unsupported file extension. Must be one of {e}",
        p=path,
        e=", ".join(CONFIG_EXTENSIONS),
    )
