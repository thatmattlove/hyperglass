For production builds, we'll want to have a real WSGI front end instead of the built in Flask developer web server. For time's sake, Ubuntu 18.04 instructions are provided. That said, this is a pretty generic setup and should be easily replicable to other platforms.

# Gunicorn Installation

Gunicorn is a WSGI server written in Python.

## Install
```console
$ pip3 install gunicorn
```

## Configure

Migrate the example Gunicorn configuration file:
```console
$ cd /opt/hyperglass/
$ python3 manage.py migrate-gunicorn
```

Open `hyperglass/hyperglass/gunicorn_config.py`, and adjust the parameters to match your local system. For example, make sure the `command` parameter matches the location of your `gunicorn` executable (`which gunicorn`), the `pythonpath` parameter matches the location where hyperglass is installed, and that the `user` parameter matches the user you're running hyperglass as:

### Permissions

Gunicorn requires read/write/executable access to the entire `hyperglass/hyperglass` directory in order to read its configuration and execute the python code. If running gunicorn as `www-data`, fix permissions with:

```console
# cd /opt/hyperglass/
# python3 manage.py update-permissions --user <user> --group <group>
```

!!! note "File Ownership"
    If the `--user` and `--group` options are not specified, `www-data` will be used.
