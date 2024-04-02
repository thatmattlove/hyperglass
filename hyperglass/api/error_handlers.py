"""API Error Handlers."""

# Third Party
from litestar import Request, Response
from litestar.exceptions import ValidationException

# Project
from hyperglass.log import log
from hyperglass.state import use_state

__all__ = (
    "default_handler",
    "http_handler",
    "app_handler",
    "validation_handler",
)


def default_handler(request: Request, exc: BaseException) -> Response:
    """Handle uncaught errors."""
    state = use_state()
    log.bind(method=request.method, path=request.url.path, detail=str(exc)).critical("Error")
    return Response(
        {"output": state.params.messages.general, "level": "danger", "keywords": []},
        status_code=500,
    )


def http_handler(request: Request, exc: BaseException) -> Response:
    """Handle web server errors."""
    log.bind(method=request.method, path=request.url.path, detail=exc.detail).critical("HTTP Error")
    return Response(
        {"output": exc.detail, "level": "danger", "keywords": []},
        status_code=exc.status_code,
    )


def app_handler(request: Request, exc: BaseException) -> Response:
    """Handle application errors."""
    log.bind(method=request.method, path=request.url.path, detail=exc.message).critical(
        "hyperglass Error"
    )
    return Response(
        {"output": exc.message, "level": exc.level, "keywords": exc.keywords},
        status_code=exc.status_code,
    )


def validation_handler(request: Request, exc: ValidationException) -> Response:
    """Handle Pydantic validation errors raised by FastAPI."""
    error = exc.errors()[0]
    log.bind(method=request.method, path=request.url.path, detail=error["msg"]).critical(
        "Validation Error"
    )
    return Response(
        {"output": error["msg"], "level": "error", "keywords": error["loc"]},
        status_code=422,
    )
