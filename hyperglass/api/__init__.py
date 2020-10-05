"""hyperglass REST API & Web UI."""

# Standard Library
import sys
from typing import List
from pathlib import Path

# Third Party
from fastapi import FastAPI
from fastapi.exceptions import ValidationError, RequestValidationError
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.openapi.utils import get_openapi
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

# Project
from hyperglass.log import log
from hyperglass.util import cpu_count
from hyperglass.constants import TRANSPORT_REST, __version__
from hyperglass.api.events import on_startup, on_shutdown
from hyperglass.api.routes import (
    docs,
    info,
    query,
    queries,
    routers,
    communities,
    import_certificate,
)
from hyperglass.exceptions import HyperglassError
from hyperglass.configuration import URL_DEV, STATIC_PATH, params, devices
from hyperglass.api.error_handlers import (
    app_handler,
    http_handler,
    default_handler,
    validation_handler,
)
from hyperglass.models.api.response import (
    QueryError,
    InfoResponse,
    QueryResponse,
    RoutersResponse,
    CommunityResponse,
    SupportedQueryResponse,
)

WORKING_DIR = Path(__file__).parent
EXAMPLES_DIR = WORKING_DIR / "examples"

UI_DIR = STATIC_PATH / "ui"
CUSTOM_DIR = STATIC_PATH / "custom"
IMAGES_DIR = STATIC_PATH / "images"

EXAMPLE_DEVICES_PY = EXAMPLES_DIR / "devices.py"
EXAMPLE_QUERIES_PY = EXAMPLES_DIR / "queries.py"
EXAMPLE_QUERY_PY = EXAMPLES_DIR / "query.py"
EXAMPLE_DEVICES_CURL = EXAMPLES_DIR / "devices.sh"
EXAMPLE_QUERIES_CURL = EXAMPLES_DIR / "queries.sh"
EXAMPLE_QUERY_CURL = EXAMPLES_DIR / "query.sh"

ASGI_PARAMS = {
    "host": str(params.listen_address),
    "port": params.listen_port,
    "debug": params.debug,
    "workers": cpu_count(2),
}
DOCS_PARAMS = {}
if params.docs.enable:
    DOCS_PARAMS.update({"openapi_url": params.docs.openapi_uri})
    if params.docs.mode == "redoc":
        DOCS_PARAMS.update({"docs_url": None, "redoc_url": params.docs.uri})
    elif params.docs.mode == "swagger":
        DOCS_PARAMS.update({"docs_url": params.docs.uri, "redoc_url": None})

for directory in (UI_DIR, IMAGES_DIR):
    if not directory.exists():
        log.warning("Directory '{d}' does not exist, creating...", d=str(directory))
        directory.mkdir()

# Main App Definition
app = FastAPI(
    debug=params.debug,
    title=params.site_title,
    description=params.site_description,
    version=__version__,
    default_response_class=JSONResponse,
    **DOCS_PARAMS,
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

# Request Validation Error Handler
app.add_exception_handler(RequestValidationError, validation_handler)

# App Validation Error Handler
app.add_exception_handler(ValidationError, validation_handler)

# Uncaught Error Handler
app.add_exception_handler(Exception, default_handler)


def _custom_openapi():
    """Generate custom OpenAPI config."""
    openapi_schema = get_openapi(
        title=params.docs.title.format(site_title=params.site_title),
        version=__version__,
        description=params.docs.description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "/images/light" + params.web.logo.light.suffix
    }

    query_samples = []
    queries_samples = []
    devices_samples = []

    with EXAMPLE_QUERY_CURL.open("r") as e:
        example = e.read()
        query_samples.append(
            {"lang": "cURL", "source": example % str(params.docs.base_url)}
        )

    with EXAMPLE_QUERY_PY.open("r") as e:
        example = e.read()
        query_samples.append(
            {"lang": "Python", "source": example % str(params.docs.base_url)}
        )

    with EXAMPLE_DEVICES_CURL.open("r") as e:
        example = e.read()
        queries_samples.append(
            {"lang": "cURL", "source": example % str(params.docs.base_url)}
        )
    with EXAMPLE_DEVICES_PY.open("r") as e:
        example = e.read()
        queries_samples.append(
            {"lang": "Python", "source": example % str(params.docs.base_url)}
        )

    with EXAMPLE_QUERIES_CURL.open("r") as e:
        example = e.read()
        devices_samples.append(
            {"lang": "cURL", "source": example % str(params.docs.base_url)}
        )

    with EXAMPLE_QUERIES_PY.open("r") as e:
        example = e.read()
        devices_samples.append(
            {"lang": "Python", "source": example % str(params.docs.base_url)}
        )

    openapi_schema["paths"]["/api/query/"]["post"]["x-code-samples"] = query_samples
    openapi_schema["paths"]["/api/devices"]["get"]["x-code-samples"] = devices_samples
    openapi_schema["paths"]["/api/queries"]["get"]["x-code-samples"] = queries_samples

    app.openapi_schema = openapi_schema
    return app.openapi_schema


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
    path="/api/info",
    endpoint=info,
    methods=["GET"],
    response_model=InfoResponse,
    response_class=JSONResponse,
    summary=params.docs.info.summary,
    description=params.docs.info.description,
    tags=[params.docs.info.title],
)

app.add_api_route(
    path="/api/devices",
    endpoint=routers,
    methods=["GET"],
    response_model=List[RoutersResponse],
    response_class=JSONResponse,
    summary=params.docs.devices.summary,
    description=params.docs.devices.description,
    tags=[params.docs.devices.title],
)

app.add_api_route(
    path="/api/communities",
    endpoint=communities,
    methods=["GET"],
    response_model=List[CommunityResponse],
    summary=params.docs.communities.summary,
    tags=[params.docs.communities.title],
)

app.add_api_route(
    path="/api/queries",
    endpoint=queries,
    methods=["GET"],
    response_class=JSONResponse,
    response_model=List[SupportedQueryResponse],
    summary=params.docs.queries.summary,
    description=params.docs.queries.description,
    tags=[params.docs.queries.title],
)

app.add_api_route(
    path="/api/query/",
    endpoint=query,
    methods=["POST"],
    summary=params.docs.query.summary,
    description=params.docs.query.description,
    responses={
        400: {"model": QueryError, "description": "Request Content Error"},
        422: {"model": QueryError, "description": "Request Format Error"},
        500: {"model": QueryError, "description": "Server Error"},
    },
    response_model=QueryResponse,
    tags=[params.docs.query.title],
    response_class=JSONResponse,
)

# Enable certificate import route only if a device using
# hyperglass-agent is defined.
if [n for n in devices.all_nos if n in TRANSPORT_REST]:
    app.add_api_route(
        path="/api/import-agent-certificate/",
        endpoint=import_certificate,
        methods=["POST"],
        include_in_schema=False,
    )

if params.docs.enable:
    app.add_api_route(path=params.docs.uri, endpoint=docs, include_in_schema=False)
    app.openapi = _custom_openapi
    log.debug("API Docs config: {}", app.openapi())

app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
app.mount("/custom", StaticFiles(directory=CUSTOM_DIR), name="custom")
app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="ui")


def start(**kwargs):
    """Start the web server with Uvicorn ASGI."""
    # Third Party
    import uvicorn

    try:
        uvicorn.run("hyperglass.api:app", **ASGI_PARAMS, **kwargs)
    except KeyboardInterrupt:
        sys.exit(1)
