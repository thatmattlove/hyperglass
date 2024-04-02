"""hyperglass API."""
# Standard Library
import logging

# Third Party
from litestar import Litestar
from litestar.openapi import OpenAPIConfig
from litestar.exceptions import HTTPException, ValidationException
from litestar.static_files import create_static_files_router

# Project
from hyperglass.state import use_state
from hyperglass.constants import __version__
from hyperglass.exceptions import HyperglassError

# Local
from .events import check_redis
from .routes import info, query, device, devices, queries
from .middleware import COMPRESSION_CONFIG, create_cors_config
from .error_handlers import app_handler, http_handler, default_handler, validation_handler

__all__ = ("app",)

STATE = use_state()

UI_DIR = STATE.settings.static_path / "ui"
IMAGES_DIR = STATE.settings.static_path / "images"


OPEN_API = OpenAPIConfig(
    title=STATE.params.docs.title.format(site_title=STATE.params.site_title),
    version=__version__,
    description=STATE.params.docs.description,
    path=STATE.params.docs.path,
    root_schema_site="elements",
)

HANDLERS = [
    device,
    devices,
    queries,
    info,
    query,
]

if not STATE.settings.disable_ui:
    HANDLERS = [
        *HANDLERS,
        create_static_files_router(
            path="/images", directories=[IMAGES_DIR], name="images", include_in_schema=False
        ),
        create_static_files_router(
            path="/", directories=[UI_DIR], name="ui", html_mode=True, include_in_schema=False
        ),
    ]


app = Litestar(
    route_handlers=HANDLERS,
    exception_handlers={
        HTTPException: http_handler,
        HyperglassError: app_handler,
        ValidationException: validation_handler,
        Exception: default_handler,
    },
    on_startup=[check_redis],
    debug=STATE.settings.debug,
    cors_config=create_cors_config(state=STATE),
    compression_config=COMPRESSION_CONFIG,
    openapi_config=OPEN_API if STATE.params.docs.enable else None,
)
