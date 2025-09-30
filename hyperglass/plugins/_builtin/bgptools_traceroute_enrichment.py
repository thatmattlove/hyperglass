"""IP enrichment for structured traceroute data."""

# Standard Library
import socket
import typing as t

# Third Party
from pydantic import PrivateAttr

# Project
from hyperglass.log import log
from hyperglass.plugins._output import OutputPlugin
from hyperglass.models.data.traceroute import TracerouteResult

if t.TYPE_CHECKING:
    from hyperglass.models.data import OutputDataModel
    from hyperglass.models.api.query import Query


class ZBgpToolsTracerouteEnrichment(OutputPlugin):
    """Enrich structured traceroute output with IP enrichment ASN/organization data and reverse DNS."""

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: t.Sequence[str] = (
        "mikrotik_routeros",
        "mikrotik_switchos",
        "mikrotik",
        "cisco_ios",
        "juniper_junos",
    )
    directives: t.Sequence[str] = ("traceroute", "MikroTik_Traceroute")
    common: bool = True

    def _enrich_ip_with_bgptools(self, ip: str) -> t.Dict[str, t.Any]:
        """Query BGP.tools whois interface for IP enrichment data."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(("bgp.tools", 43))

            query = f"begin\nverbose\n{ip}\nend\n"
            sock.sendall(query.encode())

            response = b""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data
            sock.close()

            response_text = response.decode("utf-8", errors="ignore").strip()
            log.debug(f"BGP.tools response for {ip}: {response_text}")

            if response_text and "|" in response_text:
                lines = response_text.split("\n")
                for line in lines:
                    if "|" in line and ip in line:
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) >= 7:
                            return {
                                "asn": parts[0] if parts[0] else None,
                                "org": parts[6] if len(parts) > 6 else None,
                                "prefix": parts[2] if parts[2] else None,
                                "country": parts[3] if parts[3] else None,
                                "rir": parts[4] if parts[4] else None,
                                "allocated": parts[5] if parts[5] else None,
                            }

        except Exception as e:
            log.debug(f"BGP.tools enrichment failed for {ip}: {e}")

        return {
            "asn": None,
            "org": None,
            "prefix": None,
            "country": None,
            "rir": None,
            "allocated": None,
        }

    def _reverse_dns_lookup(self, ip: str) -> t.Optional[str]:
        """Perform reverse DNS lookup for IP address."""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            log.debug(f"Reverse DNS for {ip}: {hostname}")
            return hostname
        except (socket.herror, socket.gaierror, socket.timeout) as e:
            log.debug(f"Reverse DNS lookup failed for {ip}: {e}")
            return None

    def process(self, *, output: "OutputDataModel", query: "Query") -> "OutputDataModel":
        """Enrich structured traceroute data with BGP.tools and reverse DNS information."""

        if not isinstance(output, TracerouteResult):
            return output

        _log = log.bind(plugin=self.__class__.__name__)
        _log.debug(f"Starting enrichment for {len(output.hops)} traceroute hops")

        for hop in output.hops:
            if hop.ip_address and hop.asn is None:
                bgp_data = self._enrich_ip_with_bgptools(hop.ip_address)
                hop.asn = bgp_data.get("asn")
                hop.org = bgp_data.get("org")
                hop.prefix = bgp_data.get("prefix")
                hop.country = bgp_data.get("country")
                hop.rir = bgp_data.get("rir")
                hop.allocated = bgp_data.get("allocated")

                if hop.hostname is None:
                    hop.hostname = self._reverse_dns_lookup(hop.ip_address)

        _log.debug(f"Completed enrichment for traceroute to {output.target}")
        return output
