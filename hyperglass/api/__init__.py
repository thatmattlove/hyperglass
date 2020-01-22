"""hyperglass REST API & Web UI."""

# Standard Library Imports
from pathlib import Path

# Third Party Imports
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import UJSONResponse
from starlette.staticfiles import StaticFiles

# Project Imports
from hyperglass.api.error_handlers import app_handler
from hyperglass.api.error_handlers import http_handler
from hyperglass.api.events import on_shutdown
from hyperglass.api.events import on_startup
from hyperglass.api.routes import docs
from hyperglass.api.routes import query
from hyperglass.configuration import URL_DEV
from hyperglass.configuration import params
from hyperglass.constants import __version__
from hyperglass.exceptions import HyperglassError
from hyperglass.models.response import QueryResponse
from hyperglass.util import log

STATIC_DIR = Path(__file__).parent.parent / "static"
UI_DIR = STATIC_DIR / "ui"
IMAGES_DIR = STATIC_DIR / "images"

ASGI_PARAMS = {
    "host": str(params.general.listen_address),
    "port": params.general.listen_port,
    "debug": params.general.debug,
}

# Main App Definition
app = FastAPI(
    debug=params.general.debug,
    title=params.general.site_title,
    description=params.general.site_description,
    version=__version__,
    default_response_class=UJSONResponse,
    docs_url=None,
    redoc_url=None,
    openapi_url=params.general.docs.openapi_url,
    on_shutdown=on_shutdown,
    on_startup=on_startup,
)

# HTTP Error Handler
app.add_exception_handler(StarletteHTTPException, http_handler)

# Backend Application Error Handler
app.add_exception_handler(HyperglassError, app_handler)


def _custom_openapi():
    """Generate custom OpenAPI config."""
    openapi_schema = get_openapi(
        title=params.general.site_title,
        version=__version__,
        description=params.general.site_description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = _custom_openapi

if params.general.docs.enable:
    log.debug(f"API Docs config: {app.openapi()}")

CORS_ORIGINS = params.general.cors_origins.copy()
if params.general.developer_mode:
    CORS_ORIGINS.append(URL_DEV)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.add_api_route(
    path="/api/query/",
    endpoint=query,
    methods=["POST"],
    summary=params.general.docs.endpoint_summary,
    description=params.general.docs.endpoint_description,
    response_model=QueryResponse,
    tags=[params.general.docs.group_title],
    response_class=UJSONResponse,
)
app.add_api_route(path="api/docs", endpoint=docs, include_in_schema=False)
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="ui")


def start():
    """Start the web server with Uvicorn ASGI."""
    import uvicorn

    uvicorn.run(app, **ASGI_PARAMS)
