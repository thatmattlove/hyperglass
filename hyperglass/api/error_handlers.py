"""API Error Handlers."""

# Standard Library
import typing as t

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


def get_validation_exception_detail(exc: ValidationException) -> Response:
    data: dict[str, t.Any] = {
        "level": "error",
        "status_code": 422,
        "keywords": [],
        "output": repr(exc),
    }
    if isinstance(exc.extra, dict):
        outputs = []
        kw = []
        for k, v in exc.extra.values():
            outputs = [*outputs, f"{k}: {v!r}"]
            kw = [*kw, k]
        data["output"] = "\n".join(outputs)
        data["keywords"] = kw

    if isinstance(exc.extra, list):
        data["output"] = "\n".join(str(v) for v in exc.extra)
        data["keywords"] = []

    return Response(data)


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
    log.bind(method=request.method, path=request.url.path, detail=exc).critical("Validation Error")
    return get_validation_exception_detail(exc)
