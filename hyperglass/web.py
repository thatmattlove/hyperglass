"""hyperglass web app initiator."""


def start():
    """Start the web server with Uvicorn ASGI."""
    import uvicorn
    from hyperglass.hyperglass import app, APP_PARAMS

    uvicorn.run(app, **APP_PARAMS)


app = start()
