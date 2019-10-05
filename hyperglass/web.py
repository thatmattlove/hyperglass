"""
Hyperglass web app initiator. Launches Sanic with appropriate number of
workers per their documentation (equal to number of CPU cores).
"""

# Override web server listen host & port if necessary:
host = "localhost"
port = 8001

try:
    import multiprocessing
    import os
    import tempfile
    from hyperglass import hyperglass
    from hyperglass.configuration import params
    from hyperglass.configuration import stack  # NOQA: F401
except ImportError as import_error:
    raise RuntimeError(import_error)

debug = False
access_log = True

if params.general.debug:
    debug = True
    access_log = False

workers = multiprocessing.cpu_count()


def start():
    """
    Compiles configured Sass variables to CSS, then starts Sanic web
    server.
    """
    tempdir = tempfile.TemporaryDirectory(prefix="hyperglass_")
    os.environ["prometheus_multiproc_dir"] = tempdir.name

    try:
        hyperglass.app.run(
            host=host,
            port=port,
            debug=params.general.debug,
            workers=workers,
            access_log=access_log,
        )
    except Exception as hyperglass_error:
        raise RuntimeError(hyperglass_error)


app = start()
