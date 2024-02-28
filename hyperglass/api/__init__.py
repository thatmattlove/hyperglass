"""hyperglass REST API & Web UI."""

# Standard Library
import sys
from typing import List
from pathlib import Path

# Third Party
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import ValidationError, RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# Project
from hyperglass.log import log
from hyperglass.util import cpu_count
from hyperglass.state import use_state
from hyperglass.constants import __version__
from hyperglass.models.ui import UIParameters
from hyperglass.api.events import on_startup, on_shutdown
from hyperglass.api.routes import docs, info, query, router, queries, routers, ui_props
from hyperglass.exceptions import HyperglassError
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
    SupportedQueryResponse,
)

STATE = use_state()

WORKING_DIR = Path(__file__).parent
EXAMPLES_DIR = WORKING_DIR / "examples"

UI_DIR = STATE.settings.static_path / "ui"
IMAGES_DIR = STATE.settings.static_path / "images"

EXAMPLE_DEVICES_PY = EXAMPLES_DIR / "devices.py"
EXAMPLE_QUERIES_PY = EXAMPLES_DIR / "queries.py"
EXAMPLE_QUERY_PY = EXAMPLES_DIR / "query.py"
EXAMPLE_DEVICES_CURL = EXAMPLES_DIR / "devices.sh"
EXAMPLE_QUERIES_CURL = EXAMPLES_DIR / "queries.sh"
EXAMPLE_QUERY_CURL = EXAMPLES_DIR / "query.sh"

ASGI_PARAMS = {
    "host": str(STATE.settings.host),
    "port": STATE.settings.port,
    "debug": STATE.settings.debug,
    "workers": cpu_count(2),
}
DOCS_PARAMS = {}
if STATE.params.docs.enable:
    DOCS_PARAMS.update({"openapi_url": "/openapi.json"})
    if STATE.params.docs.mode == "redoc":
        DOCS_PARAMS.update({"docs_url": None, "redoc_url": STATE.params.docs.path})
    elif STATE.params.docs.mode == "swagger":
        DOCS_PARAMS.update({"docs_url": STATE.params.docs.path, "redoc_url": None})

for directory in (UI_DIR, IMAGES_DIR):
    if not directory.exists():
        log.warning("Directory '{d}' does not exist, creating...", d=str(directory))
        directory.mkdir()

# Main App Definition
app = FastAPI(
    debug=STATE.settings.debug,
    title=STATE.params.site_title,
    description=STATE.params.site_description,
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
        title=STATE.params.docs.title.format(site_title=STATE.params.site_title),
        version=__version__,
        description=STATE.params.docs.description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": "/images/light" + STATE.params.web.logo.light.suffix}

    query_samples = []
    queries_samples = []
    devices_samples = []

    with EXAMPLE_QUERY_CURL.open("r") as e:
        example = e.read()
        query_samples.append({"lang": "cURL", "source": example % str(STATE.params.docs.base_url)})

    with EXAMPLE_QUERY_PY.open("r") as e:
        example = e.read()
        query_samples.append(
            {"lang": "Python", "source": example % str(STATE.params.docs.base_url)}
        )

    with EXAMPLE_DEVICES_CURL.open("r") as e:
        example = e.read()
        queries_samples.append(
            {"lang": "cURL", "source": example % str(STATE.params.docs.base_url)}
        )
    with EXAMPLE_DEVICES_PY.open("r") as e:
        example = e.read()
        queries_samples.append(
            {"lang": "Python", "source": example % str(STATE.params.docs.base_url)}
        )

    with EXAMPLE_QUERIES_CURL.open("r") as e:
        example = e.read()
        devices_samples.append(
            {"lang": "cURL", "source": example % str(STATE.params.docs.base_url)}
        )

    with EXAMPLE_QUERIES_PY.open("r") as e:
        example = e.read()
        devices_samples.append(
            {"lang": "Python", "source": example % str(STATE.params.docs.base_url)}
        )

    openapi_schema["paths"]["/api/query/"]["post"]["x-code-samples"] = query_samples
    openapi_schema["paths"]["/api/devices"]["get"]["x-code-samples"] = devices_samples
    openapi_schema["paths"]["/api/queries"]["get"]["x-code-samples"] = queries_samples

    app.openapi_schema = openapi_schema
    return app.openapi_schema


CORS_ORIGINS = STATE.params.cors_origins.copy()
if STATE.settings.dev_mode:
    CORS_ORIGINS = [*CORS_ORIGINS, STATE.settings.dev_url, "http://localhost:3000"]

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# GZIP Middleware
app.add_middleware(GZipMiddleware)

app.add_api_route(
    path="/api/info",
    endpoint=info,
    methods=["GET"],
    response_model=InfoResponse,
    response_class=JSONResponse,
    summary=STATE.params.docs.info.summary,
    description=STATE.params.docs.info.description,
    tags=[STATE.params.docs.info.title],
)

app.add_api_route(
    path="/api/devices",
    endpoint=routers,
    methods=["GET"],
    response_model=List[RoutersResponse],
    response_class=JSONResponse,
    summary=STATE.params.docs.devices.summary,
    description=STATE.params.docs.devices.description,
    tags=[STATE.params.docs.devices.title],
)

app.add_api_route(
    path="/api/devices/{id}",
    endpoint=router,
    methods=["GET"],
    response_model=RoutersResponse,
    response_class=JSONResponse,
    summary=STATE.params.docs.devices.summary,
    description=STATE.params.docs.devices.description,
    tags=[STATE.params.docs.devices.title],
)

app.add_api_route(
    path="/api/queries",
    endpoint=queries,
    methods=["GET"],
    response_class=JSONResponse,
    response_model=List[SupportedQueryResponse],
    summary=STATE.params.docs.queries.summary,
    description=STATE.params.docs.queries.description,
    tags=[STATE.params.docs.queries.title],
)

app.add_api_route(
    path="/api/query",
    endpoint=query,
    methods=["POST"],
    summary=STATE.params.docs.query.summary,
    description=STATE.params.docs.query.description,
    responses={
        400: {"model": QueryError, "description": "Request Content Error"},
        422: {"model": QueryError, "description": "Request Format Error"},
        500: {"model": QueryError, "description": "Server Error"},
    },
    response_model=QueryResponse,
    tags=[STATE.params.docs.query.title],
    response_class=JSONResponse,
)

app.add_api_route(
    path="/ui/props/",
    endpoint=ui_props,
    methods=["GET", "OPTIONS"],
    response_class=JSONResponse,
    response_model=UIParameters,
    response_model_by_alias=True,
)


if STATE.params.docs.enable:
    app.add_api_route(path=STATE.params.docs.path, endpoint=docs, include_in_schema=False)
    app.openapi = _custom_openapi

app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="ui")
