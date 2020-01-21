"""hyperglass web app initiator."""
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, BackgroundTasks
from fastapi import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.responses import UJSONResponse
from starlette.staticfiles import StaticFiles

from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry
from prometheus_client import Counter
from prometheus_client import generate_latest
from prometheus_client import multiprocess

from hyperglass.configuration import frontend_params
from hyperglass.configuration import params
from hyperglass.constants import __version__
from hyperglass.exceptions import AuthError
from hyperglass.exceptions import DeviceTimeout
from hyperglass.exceptions import HyperglassError
from hyperglass.exceptions import InputInvalid
from hyperglass.exceptions import InputNotAllowed
from hyperglass.exceptions import ResponseEmpty
from hyperglass.exceptions import RestError
from hyperglass.exceptions import ScrapeError
from hyperglass.models.query import Query
from hyperglass.query import handle_query, REDIS_CONFIG
from hyperglass.util import check_python
from hyperglass.util import check_redis
from hyperglass.util import log
from hyperglass.util import write_env

STATIC_DIR = Path(__file__).parent / "static"
UI_DIR = STATIC_DIR / "ui"
IMAGES_DIR = STATIC_DIR / "images"
NEXT_DIR = UI_DIR / "_next"

STATIC_FILES = "\n".join([str(STATIC_DIR), str(UI_DIR), str(IMAGES_DIR), str(NEXT_DIR)])

log.debug(f"Static Files: {STATIC_FILES}")

docs_mode_map = {"swagger": "docs_url", "redoc": "redoc_url"}

docs_config = {"docs_url": None, "redoc_url": None}

if params.general.docs.enable:
    if params.general.docs.mode == "swagger":
        docs_config["docs_url"] = params.general.docs.uri
        docs_config["redoc_url"] = None
    elif params.general.docs.mode == "redoc":
        docs_config["docs_url"] = None
        docs_config["redoc_url"] = params.general.docs.uri


# Main App Definition
app = FastAPI(
    debug=params.general.debug,
    title=params.general.site_title,
    description=params.general.site_description,
    version=__version__,
    **docs_config,
)
app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")
app.mount("/_next", StaticFiles(directory=NEXT_DIR), name="_next")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
app.mount("/ui/images", StaticFiles(directory=IMAGES_DIR), name="ui/images")

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
async def write_env_variables():
    """Write environment varibles for Next.js/Node.

    Returns:
        {bool} -- True if successful
    """
    if params.general.developer_mode:
        env_vars = {"NODE_ENV": "development", "_HYPERGLASS_URL_": DEV_URL}
    else:
        env_vars = {"NODE_ENV": "production", "_HYPERGLASS_URL_": PROD_URL}
    result = await write_env(env_vars)
    if result:
        log.debug(result)
    return True


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Handle web server errors."""
    return UJSONResponse(
        {"output": exc.detail, "alert": "danger", "keywords": []},
        status_code=exc.status_code,
    )


@app.exception_handler(HyperglassError)
async def http_exception_handler(request, exc):
    """Handle application errors."""
    return UJSONResponse(
        {"output": exc.message, "alert": exc.alert, "keywords": exc.keywords},
        status_code=400,
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


@app.get("/metrics")
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


@app.get("/api/config")
async def frontend_config():
    """Provide validated user/default config for front end consumption.

    Returns:
        {dict} -- Filtered configuration
    """
    return UJSONResponse(frontend_params, status_code=200)


@app.post("/api/query/")
async def hyperglass_main(
    query_data: Query, request: Request, background_tasks: BackgroundTasks
):
    """Process XHR POST data.

    Ingests XHR POST data from
    form submit, passes it to the backend application to perform the
    filtering/lookups.
    """

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

    try:
        response = await handle_query(query_data)
    except (InputInvalid, InputNotAllowed, ResponseEmpty) as frontend_error:
        raise HTTPException(detail=frontend_error.dict(), status_code=400)
    except (AuthError, RestError, ScrapeError, DeviceTimeout) as backend_error:
        raise HTTPException(detail=backend_error.dict(), status_code=500)

    return UJSONResponse({"output": response}, status_code=200)


def start():
    """Start the web server with Uvicorn ASGI."""
    import uvicorn

    uvicorn.run(app, **ASGI_PARAMS)


app = start()
