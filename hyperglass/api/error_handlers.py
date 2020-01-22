"""API Error Handlers."""
# Third Party Imports
from starlette.responses import UJSONResponse


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
