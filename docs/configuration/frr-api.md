# Add User

```console
# useradd -M hyperglass-frr-api
# usermod -L hyerglass-frr-api
```

```console
# chown -R hyerglass-frr-api:hyerglass-frr-api /opt/hyperglass-frr
```
iptables -A INPUT -i loopback1 -s 199.34.92.72 -p tcp --dport 8080 -J ACCEPT

Add user to fttvty group:

```console
# usermod -a -G <group> <user>
```
