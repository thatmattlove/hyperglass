"""IP enrichment for structured traceroute data."""

# Standard Library
import asyncio
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


class ZTracerouteIpEnrichment(OutputPlugin):
    """Enrich structured traceroute output with IP enrichment ASN/organization data and reverse DNS."""

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: t.Sequence[str] = (
        "mikrotik_routeros",
        "mikrotik_switchos",
        "mikrotik",
        "cisco_ios",
        "juniper_junos",
        "huawei",
        "huawei_vrpv8",
    )
    directives: t.Sequence[str] = ("traceroute", "MikroTik_Traceroute")
    common: bool = True

    def _reverse_dns_lookup(self, ip: str) -> t.Optional[str]:
        """Perform reverse DNS lookup for an IP address."""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            log.debug(f"Reverse DNS for {ip}: {hostname}")
            return hostname
        except (socket.herror, socket.gaierror, socket.timeout) as e:
            log.debug(f"Reverse DNS lookup failed for {ip}: {e}")
            return None

    async def _enrich_async(self, output: TracerouteResult) -> None:
        """Async helper to enrich traceroute data."""
        # First enrich with IP information (ASN numbers)
        await output.enrich_with_ip_enrichment()

        # Then enrich ASN numbers with organization names
        await output.enrich_asn_organizations()

    def process(self, *, output: "OutputDataModel", query: "Query") -> "OutputDataModel":
        """Enrich structured traceroute data with IP enrichment and reverse DNS information."""

        if not isinstance(output, TracerouteResult):
            return output

        _log = log.bind(plugin=self.__class__.__name__)
        _log.debug(f"Starting IP enrichment for {len(output.hops)} traceroute hops")

        # Check if IP enrichment is enabled in config
        try:
            from hyperglass.state import use_state

            params = use_state("params")
            # If structured config missing or traceroute enrichment disabled, skip
            # IP enrichment but still perform reverse DNS lookups.
            if (
                not getattr(params, "structured", None)
                or not params.structured.ip_enrichment.enrich_traceroute
                or getattr(params.structured, "enable_for_traceroute", None) is False
            ):
                _log.debug("IP enrichment for traceroute disabled in configuration")
                # Still do reverse DNS if enrichment is disabled
                for hop in output.hops:
                    if hop.ip_address and hop.hostname is None:
                        hop.hostname = self._reverse_dns_lookup(hop.ip_address)
                return output
        except Exception as e:
            _log.debug(f"Could not check IP enrichment config: {e}")

        # Use the built-in enrichment method from TracerouteResult
        try:
            # Run async enrichment in sync context
            loop = None
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an event loop, create a new task
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._enrich_async(output))
                        future.result()
                else:
                    loop.run_until_complete(self._enrich_async(output))
            except RuntimeError:
                # No event loop, create one
                asyncio.run(self._enrich_async(output))
            _log.debug("IP enrichment completed successfully")
        except Exception as e:
            _log.error(f"IP enrichment failed: {e}")

        # Add reverse DNS lookups for any hops that don't have hostnames
        for hop in output.hops:
            if hop.ip_address and hop.hostname is None:
                hop.hostname = self._reverse_dns_lookup(hop.ip_address)

        _log.debug(f"Completed enrichment for traceroute to {output.target}")
        return output
