"""hyperglass REST API & Web UI."""

# Standard Library Imports
from pathlib import Path

# Third Party Imports
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import UJSONResponse
from starlette.staticfiles import StaticFiles

# Project Imports
from hyperglass.api.error_handlers import app_handler
from hyperglass.api.error_handlers import default_handler
from hyperglass.api.error_handlers import http_handler
from hyperglass.api.error_handlers import validation_handler
from hyperglass.api.events import on_shutdown
from hyperglass.api.events import on_startup
from hyperglass.api.models.response import QueryResponse
from hyperglass.api.routes import docs
from hyperglass.api.routes import queries
from hyperglass.api.routes import query
from hyperglass.api.routes import routers
from hyperglass.configuration import URL_DEV
from hyperglass.configuration import params
from hyperglass.constants import __version__
from hyperglass.exceptions import HyperglassError
from hyperglass.util import log

STATIC_DIR = Path(__file__).parent.parent / "static"
UI_DIR = STATIC_DIR / "ui"
IMAGES_DIR = STATIC_DIR / "images"

ASGI_PARAMS = {
    "host": str(params.listen_address),
    "port": params.listen_port,
    "debug": params.debug,
}

# Main App Definition
app = FastAPI(
    debug=params.debug,
    title=params.site_title,
    description=params.site_description,
    version=__version__,
    default_response_class=UJSONResponse,
    docs_url=None,
    redoc_url=None,
    openapi_url=params.docs.openapi_url,
)

# Add Event Handlers
for startup in on_startup:
    app.add_event_handler("startup", startup)

for shutdown in on_shutdown:
    app.add_event_handler("shutdown", shutdown)

# HTTP Error Handler
app.add_exception_handler(StarletteHTTPException, http_handler)

# Backend Application Error Handler
app.add_exception_handler(HyperglassError, app_handler)

# Validation Error Handler
app.add_exception_handler(RequestValidationError, validation_handler)

# Uncaught Error Handler
app.add_exception_handler(Exception, default_handler)


def _custom_openapi():
    """Generate custom OpenAPI config."""
    openapi_schema = get_openapi(
        title=params.site_title,
        version=__version__,
        description=params.site_description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = _custom_openapi

if params.docs.enable:
    log.debug(f"API Docs config: {app.openapi()}")

CORS_ORIGINS = params.cors_origins.copy()
if params.developer_mode:
    CORS_ORIGINS.append(URL_DEV)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.add_api_route(
    path="/api/devices", endpoint=routers, methods=["GET"], response_class=UJSONResponse
)
app.add_api_route(
    path="/api/queries", endpoint=queries, methods=["GET"], response_class=UJSONResponse
)
app.add_api_route(
    path="/api/query/",
    endpoint=query,
    methods=["POST"],
    summary=params.docs.endpoint_summary,
    description=params.docs.endpoint_description,
    response_model=QueryResponse,
    tags=[params.docs.group_title],
    response_class=UJSONResponse,
)
app.add_api_route(path="/api/docs", endpoint=docs, include_in_schema=False)
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="ui")


def start():
    """Start the web server with Uvicorn ASGI."""
    import uvicorn

    uvicorn.run(app, **ASGI_PARAMS)
