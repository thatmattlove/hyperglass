"""IP enrichment for structured BGP route data - show path functionality."""

# Standard Library
import asyncio
import typing as t

# Third Party
from pydantic import PrivateAttr

# Project
from hyperglass.log import log
from hyperglass.plugins._output import OutputPlugin
from hyperglass.models.data.bgp_route import BGPRouteTable

if t.TYPE_CHECKING:
    from hyperglass.models.data import OutputDataModel
    from hyperglass.models.api.query import Query


class ZBgpRouteIpEnrichment(OutputPlugin):
    """Enrich structured BGP route output with IP enrichment for next-hop ASN/organization data."""

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: t.Sequence[str] = (
        "mikrotik_routeros",
        "mikrotik_switchos",
        "mikrotik",
        "cisco_ios",
        "juniper_junos",
        "arista_eos",
        "frr",
        "huawei",
        "huawei_vrpv8",
    )
    directives: t.Sequence[str] = ("bgp_route", "bgp_community")
    common: bool = True

    async def _enrich_async(self, output: BGPRouteTable, enrich_next_hop: bool = True) -> None:
        """Async helper to enrich BGP route data."""
        _log = log.bind(plugin=self.__class__.__name__)

        if enrich_next_hop:
            try:
                # First enrich with next-hop IP information (if enabled)
                await output.enrich_with_ip_enrichment()
                _log.debug("BGP next-hop IP enrichment completed")
            except Exception as e:
                _log.error(f"BGP next-hop IP enrichment failed: {e}")
        else:
            _log.debug("BGP next-hop IP enrichment skipped (disabled in config)")

        try:
            # Always enrich AS path ASNs with organization names
            await output.enrich_as_path_organizations()
            _log.debug("BGP AS path organization enrichment completed")
        except Exception as e:
            _log.error(f"BGP AS path organization enrichment failed: {e}")

    def process(self, *, output: "OutputDataModel", query: "Query") -> "OutputDataModel":
        """Enrich structured BGP route data with next-hop IP enrichment information."""

        if not isinstance(output, BGPRouteTable):
            return output

        _log = log.bind(plugin=self.__class__.__name__)
        _log.warning(f"🔍 BGP ROUTE PLUGIN STARTED - Processing {len(output.routes)} BGP routes")

        # Check if IP enrichment is enabled in config
        enrich_next_hop = True
        try:
            from hyperglass.state import use_state

            params = use_state("params")
            if not params.structured.ip_enrichment.enabled:
                _log.debug("IP enrichment disabled in configuration")
                return output

            # Check next-hop enrichment setting but don't exit - we still want ASN org enrichment
            enrich_next_hop = params.structured.ip_enrichment.enrich_next_hop
            if not enrich_next_hop:
                _log.debug(
                    "Next-hop enrichment disabled in configuration - will skip next-hop lookup but continue with ASN organization enrichment"
                )
        except Exception as e:
            _log.debug(f"Could not check IP enrichment config: {e}")

        # Use the built-in enrichment method from BGPRouteTable
        try:
            # Run async enrichment in sync context
            loop = None
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an event loop, create a new task
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run, self._enrich_async(output, enrich_next_hop)
                        )
                        future.result()
                else:
                    loop.run_until_complete(self._enrich_async(output, enrich_next_hop))
            except RuntimeError:
                # No event loop, create one
                asyncio.run(self._enrich_async(output, enrich_next_hop))
            _log.warning(
                f"🔍 BGP ROUTE PLUGIN COMPLETED - ASN organizations: {len(output.asn_organizations)}"
            )
        except Exception as e:
            _log.error(f"BGP route IP enrichment failed: {e}")

        _log.debug(f"Completed enrichment for BGP routes")
        return output
