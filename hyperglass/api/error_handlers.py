"""API Error Handlers."""

# Third Party
from fastapi import Request
from starlette.responses import JSONResponse

# Project
from hyperglass.log import log
from hyperglass.state import use_state


async def default_handler(request: Request, exc: BaseException) -> JSONResponse:
    """Handle uncaught errors."""
    state = use_state()
    log.critical(
        "{method} {path} {detail!s}", method=request.method, path=request.url.path, detail=exc
    )
    return JSONResponse(
        {"output": state.params.messages.general, "level": "danger", "keywords": []},
        status_code=500,
    )


async def http_handler(request: Request, exc: BaseException) -> JSONResponse:
    """Handle web server errors."""
    log.critical(
        "{method} {path} {detail}", method=request.method, path=request.url.path, detail=exc.detail
    )
    return JSONResponse(
        {"output": exc.detail, "level": "danger", "keywords": []},
        status_code=exc.status_code,
    )


async def app_handler(request: Request, exc: BaseException) -> JSONResponse:
    """Handle application errors."""
    log.critical(
        "{method} {path} {detail}", method=request.method, path=request.url.path, detail=exc.message
    )
    return JSONResponse(
        {"output": exc.message, "level": exc.level, "keywords": exc.keywords},
        status_code=exc.status_code,
    )


async def validation_handler(request: Request, exc: BaseException) -> JSONResponse:
    """Handle Pydantic validation errors raised by FastAPI."""
    error = exc.errors()[0]
    log.critical(
        "{method} {path} {detail}",
        method=request.method,
        path=request.url.path,
        detail=error["msg"],
    )
    return JSONResponse(
        {"output": error["msg"], "level": "error", "keywords": error["loc"]},
        status_code=422,
    )
