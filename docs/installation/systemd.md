More than likely, you'll want to run Hyperglass as a service so that it automatically starts on server boot. Any service manager can be used, however Ubuntu `systemd` instructions are included as a reference.

For easy installation, migrate the example `systemd` service:

```console
$ cd /opt/hyperglass/
$ python3 manage.py migratesystemd
```

This copies the example systemd service to `/etc/systemd/system/hyperglass.service`

#### Example
```ini
[Unit]
Description=Hyperglass
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/hyperglass
ExecStart=/usr/local/bin/gunicorn -c /opt/hyperglass/hyperglass/gunicorn_config.py hyperglass.wsgi

[Install]
WantedBy=multi-user.target
```
