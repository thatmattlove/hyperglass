"""Session handler for RIPEStat Data API."""

# Standard Library
from ipaddress import ip_address, ip_network

# Project
from hyperglass.log import log
from hyperglass.external._base import BaseExternal


class RIPEStat(BaseExternal, name="RIPEStat"):
    """RIPEStat session handler."""

    def __init__(self):
        """Initialize external base class with RIPEStat connection details."""

        super().__init__(
            base_url="https://stat.ripe.net", uri_prefix="/data", uri_suffix="data.json"
        )

    def network_info_sync(self, resource, serialize=False):
        """Get network info via RIPE's Network Info API endpoint (synchronously).

        See: https://stat.ripe.net/docs/data_api#network-info
        """
        try:
            valid_ip = ip_address(resource)

            if not valid_ip.is_global:
                log.debug("IP {ip} is not a global address", ip=str(valid_ip))
                return {"prefix": None, "asn": None}

        except ValueError:
            log.debug("'{resource}' is not a valid IP address", resource=resource)
            return {"prefix": None, "asn": None}

        raw = self._get(endpoint="network-info", params={"resource": valid_ip})

        data = {
            "asns": raw["data"]["asns"],
            "prefix": ip_network(raw["data"]["prefix"]),
        }

        if serialize:
            data["prefix"] = str(data["prefix"])
            data["asns"] = data["asns"][0]

        log.debug("Collected network info from RIPEState: {i}", i=str(data))
        return data

    async def network_info(self, resource, serialize=False):
        """Get network info via RIPE's Network Info API endpoint.

        See: https://stat.ripe.net/docs/data_api#network-info
        """
        try:
            valid_ip = ip_address(resource)

            if not valid_ip.is_global:
                log.debug("IP {ip} is not a global address", ip=str(valid_ip))
                return {"prefix": None, "asn": None}

        except ValueError:
            log.debug("'{resource}' is not a valid IP address", resource=resource)
            return {"prefix": None, "asn": None}

        raw = await self._aget(endpoint="network-info", params={"resource": valid_ip})

        data = {
            "asns": raw["data"]["asns"],
            "prefix": ip_network(raw["data"]["prefix"]),
        }

        if serialize:
            data["prefix"] = str(data["prefix"])
            data["asns"] = data["asns"][0]

        log.debug("Collected network info from RIPEState: {i}", i=str(data))
        return data
