"""hyperglass web app initiator."""
# Standard Library Imports
import os
import tempfile
from pathlib import Path

# Third Party Imports
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry
from prometheus_client import Counter
from prometheus_client import generate_latest
from prometheus_client import multiprocess
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.responses import UJSONResponse
from starlette.staticfiles import StaticFiles

# Project Imports
from hyperglass.configuration import frontend_params
from hyperglass.configuration import params
from hyperglass.constants import __version__
from hyperglass.exceptions import HyperglassError
from hyperglass.models.query import Query
from hyperglass.models.response import QueryResponse
from hyperglass.query import REDIS_CONFIG
from hyperglass.query import handle_query
from hyperglass.util import build_frontend
from hyperglass.util import check_python
from hyperglass.util import check_redis
from hyperglass.util import clear_redis_cache
from hyperglass.util import log

STATIC_DIR = Path(__file__).parent / "static"
UI_DIR = STATIC_DIR / "ui"
IMAGES_DIR = STATIC_DIR / "images"
NEXT_DIR = UI_DIR / "_next"
INDEX = UI_DIR / "index.html"

STATIC_FILES = "\n".join([str(STATIC_DIR), str(UI_DIR), str(IMAGES_DIR), str(NEXT_DIR)])

log.debug(f"Static Files: {STATIC_FILES}")

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
)
# app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")
# app.mount("/ui/images", StaticFiles(directory=IMAGES_DIR), name="ui/images")
app.mount("/_next", StaticFiles(directory=NEXT_DIR), name="_next")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

if params.general.docs.enable:
    log.debug(f"API Docs config: {app.openapi()}")

DEV_URL = f"http://localhost:{str(params.general.listen_port)}/api/"
PROD_URL = "/api/"

CORS_ORIGINS = params.general.cors_origins.copy()
if params.general.developer_mode:
    CORS_ORIGINS.append(DEV_URL)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def custom_openapi():
    """Generate custom OpenAPI config."""
    openapi_schema = get_openapi(
        title=params.general.site_title,
        version=__version__,
        description=params.general.site_description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

ASGI_PARAMS = {
    "host": str(params.general.listen_address),
    "port": params.general.listen_port,
    "debug": params.general.debug,
}


@app.on_event("startup")
async def check_python_version():
    """Ensure Python version meets minimum requirement.

    Raises:
        HyperglassError: Raised if Python version is invalid.
    """
    try:
        python_version = check_python()
        log.info(f"Python {python_version} detected")
    except RuntimeError as r:
        raise HyperglassError(str(r), alert="danger") from None


@app.on_event("startup")
async def check_redis_instance():
    """Ensure Redis is running before starting server.

    Raises:
        HyperglassError: Raised if Redis is not running.

    Returns:
        {bool} -- True if Redis is running.
    """
    try:
        await check_redis(db=params.features.cache.redis_id, config=REDIS_CONFIG)
    except RuntimeError as e:
        raise HyperglassError(str(e), alert="danger") from None

    log.debug(f"Redis is running at: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
    return True


@app.on_event("startup")
async def build_ui():
    """Perform a UI build prior to starting the application.

    Raises:
        HTTPException: Raised if any build errors occur.

    Returns:
        {bool} -- True if successful.
    """
    try:
        await build_frontend(
            dev_mode=params.general.developer_mode,
            dev_url=DEV_URL,
            prod_url=PROD_URL,
            params=frontend_params,
        )
    except RuntimeError as e:
        raise HTTPException(detail=str(e), status_code=500)
    return True


@app.on_event("shutdown")
async def clear_cache():
    """Clear the Redis cache on shutdown."""
    try:
        await clear_redis_cache(db=params.features.cache.redis_id, config=REDIS_CONFIG)
    except RuntimeError as e:
        log.error(str(e))
        pass


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Handle web server errors."""
    return UJSONResponse(
        {"output": exc.detail, "alert": "danger", "keywords": []},
        status_code=exc.status_code,
    )


@app.exception_handler(HyperglassError)
async def app_exception_handler(request, exc):
    """Handle application errors."""
    return UJSONResponse(
        {"output": exc.message, "alert": exc.alert, "keywords": exc.keywords},
        status_code=exc.status_code,
    )


# Prometheus Config
count_data = Counter(
    "count_data", "Query Counter", ["source", "query_type", "loc_id", "target", "vrf"]
)

count_errors = Counter(
    "count_errors",
    "Error Counter",
    ["reason", "source", "query_type", "loc_id", "target"],
)

count_ratelimit = Counter(
    "count_ratelimit", "Rate Limit Counter", ["message", "source"]
)

count_notfound = Counter(
    "count_notfound", "404 Not Found Counter", ["message", "path", "source"]
)

tempdir = tempfile.TemporaryDirectory(prefix="hyperglass_")
os.environ["prometheus_multiproc_dir"] = tempdir.name


@app.get("/metrics", include_in_schema=False)
async def metrics(request):
    """Serve Prometheus metrics."""
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    latest = generate_latest(registry)
    return PlainTextResponse(
        latest,
        headers={
            "Content-Type": CONTENT_TYPE_LATEST,
            "Content-Length": str(len(latest)),
        },
    )


@app.post(
    "/api/query/",
    summary=params.general.docs.endpoint_summary,
    description=params.general.docs.endpoint_description,
    response_model=QueryResponse,
    tags=[params.general.docs.group_title],
)
async def query(query_data: Query, request: Request):
    """Ingest request data pass it to the backend application to perform the query."""

    # Get client IP address for Prometheus logging & rate limiting
    client_addr = request.client.host

    # Increment Prometheus counter
    count_data.labels(
        client_addr,
        query_data.query_type,
        query_data.query_location,
        query_data.query_target,
        query_data.query_vrf,
    ).inc()

    log.debug(f"Client Address: {client_addr}")

    response = await handle_query(query_data)

    return UJSONResponse({"output": response}, status_code=200)


@app.get("/api/docs", include_in_schema=False)
async def docs():
    """Serve custom docs."""
    if params.general.docs.enable:
        docs_func_map = {"swagger": get_swagger_ui_html, "redoc": get_redoc_html}
        docs_func = docs_func_map[params.general.docs.mode]
        return docs_func(openapi_url=app.openapi_url, title=app.title + " - API Docs")
    else:
        raise HTTPException(detail="Not found", status_code=404)


app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="ui")


def start():
    """Start the web server with Uvicorn ASGI."""
    import uvicorn

    uvicorn.run(app, **ASGI_PARAMS)
