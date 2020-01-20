"""hyperglass web app initiator."""


def start():
    """Start the web server with Uvicorn ASGI."""
    import uvicorn
    from hyperglass.hyperglass import app, ASGI_PARAMS

    uvicorn.run(app, **ASGI_PARAMS)


app = start()
