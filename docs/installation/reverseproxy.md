More than likely, you'll be exposing Hyperglass to the internet. It is recommended practice to run most web applications behind a reverse proxy, such as Nginx, Apache, Caddy, etc. This example uses Nginx, but can easily be adapted to other reverse proxy applications if you prefer.

#### Example

The below Nginx example assumes the default [Gunicorn](installation/wsgi) settings are used.

```nginx
geo $not_prometheus_hosts {
  default 1;
  192.0.2.1/32 0;
}
server {
  listen 80;
  listen [::]:80 ipv6only=on;

  client_max_body_size 1024;

  server_name lg.domain.tld;

  location /metrics {
    if ($not_prometheus_hosts) {
      rewrite /metrics /getyourownmetrics;
    }
    try_files $uri @proxy_to_app;
  }

  location /static/ {
    alias /opt/hyperglass/hyperglass/static/;
  }

  location / {
      try_files $uri @proxy_to_app;
  }

  location @proxy_to_app {
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Host $http_host;
    proxy_redirect off;
    proxy_pass http://[::1]:8001;
  }

}
```

This configuration, in combination with the default Gunicorn configuration, makes the hyperglass front-end dual stack IPv4/IPv6 capable. To add SSL support, Nginx can be easily adjusted to terminate front-end SSL connections:

```nginx
geo $not_prometheus_hosts {
  default 1;
  192.0.2.1/32 0;
}
server {
  listen 80;
  listen [::]:80;
  server_name lg.domain.tld;
  return 301 https://$host$request_uri;
}
server {

  listen [::]:443 ssl ipv6only=on;
  listen 443 ssl;
  ssl_certificate <path to certificate>;
  ssl_certificate_key <path to private key>;

  client_max_body_size 1024;

  server_name lg.domain.tld;

  location /metrics {
    if ($not_prometheus_hosts) {
      rewrite /metrics /getyourownmetrics;
    }
    try_files $uri @proxy_to_app;
  }

  location /static/ {
    alias /opt/hyperglass/hyperglass/static/;
  }

  location / {
      try_files $uri @proxy_to_app;
  }

  location @proxy_to_app {
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Host $http_host;
    proxy_redirect off;
    proxy_pass http://[::1]:8001;
  }

}
```

[Let's Encrypt](https://letsencrypt.org/) provides automatic (and free) SSL certificate generation and renewal. There are a number of guides available on how to integrate Let's Encrypt with Nginx (or your reverse proxy of choice). Some examples:

- Digital Ocean: [How To Secure Nginx with Let's Encrypt on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-18-04)
- NGINX: [Using Free Let’s Encrypt SSL/TLS Certificates with NGINX](https://www.nginx.com/blog/using-free-ssltls-certificates-from-lets-encrypt-with-nginx/)


The `/metrics` block will ensure that hosts defined in the `geo $not_prometheus_hosts` directive are allowed to reach the `/metrics` URI, but that any other hosts will have the a request for `/metrics` rewritten to `/getyourownmetrics`, which will render the 404 error page.
