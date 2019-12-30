"""
Hyperglass web app initiator. Launches Sanic with appropriate number of
workers per their documentation (equal to number of CPU cores).
"""
try:
    import os
    import tempfile
    from hyperglass import hyperglass, APP_PARAMS
except ImportError as import_error:
    raise RuntimeError(import_error)


def start():
    """
    Compiles configured Sass variables to CSS, then starts Sanic web
    server.
    """
    tempdir = tempfile.TemporaryDirectory(prefix="hyperglass_")
    os.environ["prometheus_multiproc_dir"] = tempdir.name

    try:
        hyperglass.app.run(**APP_PARAMS)
    except Exception as hyperglass_error:
        raise RuntimeError(hyperglass_error)


app = start()
