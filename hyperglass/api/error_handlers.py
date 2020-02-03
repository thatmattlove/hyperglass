"""API Error Handlers."""

# Third Party
from starlette.responses import UJSONResponse

# Project
from hyperglass.configuration import params


async def default_handler(request, exc):
    """Handle uncaught errors."""
    return UJSONResponse(
        {"output": params.messages.general, "level": "danger", "keywords": []},
        status_code=500,
    )


async def http_handler(request, exc):
    """Handle web server errors."""
    return UJSONResponse(
        {"output": exc.detail, "level": "danger", "keywords": []},
        status_code=exc.status_code,
    )


async def app_handler(request, exc):
    """Handle application errors."""
    return UJSONResponse(
        {"output": exc.message, "level": exc.level, "keywords": exc.keywords},
        status_code=exc.status_code,
    )


async def validation_handler(request, exc):
    """Handle Pydantic validation errors raised by FastAPI."""
    error = exc.errors()[0]
    return UJSONResponse(
        {"output": error["msg"], "level": "error", "keywords": error["loc"]},
        status_code=422,
    )
