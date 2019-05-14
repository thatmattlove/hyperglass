For production builds, we'll want to have a real WSGI front end instead of the built in Flask developer web server. For time's sake, Ubuntu 18.04 instructions are provided. That said, this is a pretty generic setup and should be easily replicable to other platforms.

# Gunicorn Installation

Gunicorn is a WSGI server written in Python.

## Install
```console
# pip3 install gunicorn
```

## Configure

Locate your `gunicorn` executable with `which gunicorn`.

### Permissions

Gunicorn requires read/write/executable access to the entire `hyperglass/hyperglass` directory in order to read its configuration and execute the python code. If running gunicorn as www-data, fix permissions with:

```console
# chown -R www-data:www-data /opt/hyperglass/hyperglass
# chmod -R 744 /opt/hyperglass/hyperglass
```

<!-- # Supervisor Installation

To make cross-platform service functionality easier, it is recommended to use [`supervisord`](http://supervisord.org/) to manage the Hyperglass application. If you prefer, `systemd` or your service manager of choice may be used.

Install supervisord:

```console
# apt install -y supervisor
```

Create supervisord configuration for Hyperglass:

```console
# nano /etc/supervisor/conf.d/hyperglass.conf
[program:hyperglass]
command = /usr/local/bin/gunicorn -c /opt/hyperglass/hyperglass/gunicorn_config.py hyperglass.wsgi
directory = /opt/hyperglass/
user = www-data
```

Start supervisord:

```console
# systemctl start supervisor
# systemctl status supervisor
``` -->
