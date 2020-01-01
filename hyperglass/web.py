"""hyperglass web app initiator."""


def start():
    """Start Sanic web server."""
    try:
        from hyperglass import hyperglass, APP_PARAMS

        hyperglass.app.run(**APP_PARAMS)

    except ImportError as import_err:
        raise RuntimeError(str(import_err))
    except Exception as web_err:
        raise RuntimeError(str(web_err))


app = start()
