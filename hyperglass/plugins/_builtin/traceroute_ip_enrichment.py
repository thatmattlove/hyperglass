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
        from hyperglass.settings import Settings

        try:
            hostname = socket.gethostbyaddr(ip)[0]
            if Settings.debug:
                log.debug(f"Reverse DNS for {ip}: {hostname}")
            return hostname
        except (socket.herror, socket.gaierror, socket.timeout) as e:
            if Settings.debug:
                log.debug(f"Reverse DNS lookup failed for {ip}: {e}")
            return None

    async def _reverse_dns_lookup_async(self, ip: str) -> t.Optional[str]:
        """Async wrapper around synchronous reverse DNS lookup using a thread.

        Uses asyncio.to_thread to avoid blocking the event loop and allows
        multiple lookups to be scheduled concurrently.
        """
        try:
            return await asyncio.to_thread(self._reverse_dns_lookup, ip)
        except Exception as e:
            from hyperglass.settings import Settings

            if Settings.debug:
                log.debug(f"Reverse DNS async lookup error for {ip}: {e}")
            return None

    async def _enrich_async(self, output: TracerouteResult) -> None:
        """Async helper to enrich traceroute data.

        This performs IP enrichment (ASN lookups), ASN organization lookups,
        and then runs reverse DNS lookups concurrently for hops missing hostnames.
        """
        # First enrich with IP information (ASN numbers)
        await output.enrich_with_ip_enrichment()

        # Then enrich ASN numbers with organization names
        await output.enrich_asn_organizations()

        # Concurrent reverse DNS for hops missing hostnames
        ips_to_lookup: list[str] = [
            hop.ip_address for hop in output.hops if hop.ip_address and hop.hostname is None
        ]
        if not ips_to_lookup:
            return

        # Schedule lookups concurrently
        tasks = [asyncio.create_task(self._reverse_dns_lookup_async(ip)) for ip in ips_to_lookup]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Apply results back to hops in order
        idx = 0
        for hop in output.hops:
            if hop.ip_address and hop.hostname is None:
                res = results[idx]
                idx += 1
                if isinstance(res, Exception):
                    from hyperglass.settings import Settings

                    if Settings.debug:
                        log.debug(f"Reverse DNS lookup raised for {hop.ip_address}: {res}")
                else:
                    hop.hostname = res

    def process(self, *, output: "OutputDataModel", query: "Query") -> "OutputDataModel":
        """Enrich structured traceroute data with IP enrichment and reverse DNS information."""

        if not isinstance(output, TracerouteResult):
            return output

        _log = log.bind(plugin=self.__class__.__name__)

        # Import Settings for debug gating
        from hyperglass.settings import Settings

        _log.info(
            f"Starting IP enrichment for {len(output.hops)} traceroute hops"
        )  # Check if IP enrichment is enabled in config
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
                if Settings.debug:
                    _log.debug("IP enrichment for traceroute disabled in configuration")
                # Still do reverse DNS if enrichment is disabled
                # Perform concurrent reverse DNS lookups for hops needing hostnames
                ips = [
                    hop.ip_address for hop in output.hops if hop.ip_address and hop.hostname is None
                ]
                if ips:
                    try:
                        # Run lookups in an event loop
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                # We're inside an event loop; run tasks via asyncio.run in thread
                                import concurrent.futures

                                with concurrent.futures.ThreadPoolExecutor() as executor:
                                    future = executor.submit(
                                        lambda: asyncio.run(
                                            asyncio.gather(
                                                *[self._reverse_dns_lookup_async(ip) for ip in ips]
                                            )
                                        )
                                    )
                                    results = future.result()
                            else:
                                results = loop.run_until_complete(
                                    asyncio.gather(
                                        *[self._reverse_dns_lookup_async(ip) for ip in ips]
                                    )
                                )
                        except RuntimeError:
                            results = asyncio.run(
                                asyncio.gather(*[self._reverse_dns_lookup_async(ip) for ip in ips])
                            )

                        # Apply results
                        idx = 0
                        for hop in output.hops:
                            if hop.ip_address and hop.hostname is None:
                                res = results[idx]
                                idx += 1
                                if not isinstance(res, Exception):
                                    hop.hostname = res
                    except Exception as e:
                        if Settings.debug:
                            _log.debug(
                                f"Concurrent reverse DNS failed (fallback to sequential): {e}"
                            )
                        for hop in output.hops:
                            if hop.ip_address and hop.hostname is None:
                                hop.hostname = self._reverse_dns_lookup(hop.ip_address)
                return output
        except Exception as e:
            if Settings.debug:
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
            _log.info("IP enrichment completed successfully")
        except Exception as e:
            _log.error(f"IP enrichment failed: {e}")

        # Reverse DNS lookups already handled in _enrich_async for missing hostnames

        _log.info(f"Completed enrichment for traceroute to {output.target}")
        return output
