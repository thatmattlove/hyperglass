For production builds, we'll want to have a real WSGI front end instead of the built in Flask developer web server. For time's sake, Ubuntu 18.04 instructions are provided. That said, this is a pretty generic setup and should be easily replicable to other platforms.

# Gunicorn Installation

Gunicorn is a WSGI server written in Python.

## Install
```console
# pip3 install gunicorn
```

## Configure

Locate your `gunicorn` executable with `which gunicorn`
