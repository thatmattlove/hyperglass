"""Enhanced execution with IP enrichment."""

# Standard Library
import typing as t

# Project
from hyperglass.log import log
from hyperglass.state import use_state
from hyperglass.models.data import BGPRouteTable, TracerouteResult, OutputDataModel


async def enrich_output_with_ip_enrichment(output: OutputDataModel) -> OutputDataModel:
    """Enrich output data with IP enrichment information."""
    params = use_state("params")

    # Check if IP enrichment is enabled in configuration
    if not params.structured.ip_enrichment.enabled:
        log.debug("IP enrichment disabled in configuration, skipping")
        return output

    _log = log.bind(enrichment="ip_enrichment")
    _log.debug("Starting IP enrichment")

    try:
        if isinstance(output, BGPRouteTable):
            if params.structured.ip_enrichment.enrich_next_hop:
                _log.debug("Enriching BGP route table with next-hop information")
                await output.enrich_with_ip_enrichment()
                _log.info(f"Enriched {len(output.routes)} BGP routes with next-hop data")
            else:
                _log.debug("Next-hop enrichment disabled, skipping BGP enrichment")

        elif isinstance(output, TracerouteResult):
            if params.structured.ip_enrichment.enrich_traceroute:
                _log.debug("Enriching traceroute hops with ASN information")
                await output.enrich_with_ip_enrichment()

                # Count enriched hops
                enriched_hops = sum(1 for hop in output.hops if hop.asn and hop.asn != "None")
                _log.info(
                    f"Enriched {enriched_hops}/{len(output.hops)} traceroute hops with ASN data"
                )
            else:
                _log.debug("Traceroute enrichment disabled, skipping traceroute enrichment")

        _log.debug("IP enrichment completed successfully")

    except Exception as err:
        _log.error(f"IP enrichment failed: {err}")
        # Don't fail the entire request if enrichment fails

    return output


def format_enriched_bgp_output(route_table: BGPRouteTable) -> str:
    """Format enriched BGP route table for display."""
    if not route_table.routes:
        return "No routes found."

    lines = []
    lines.append(f"BGP Route Table (VRF: {route_table.vrf})")
    lines.append(f"Total Routes: {route_table.count}")
    lines.append("-" * 80)

    for route in route_table.routes:
        lines.append(f"Prefix: {route.prefix}")
        lines.append(f"  Active: {'Yes' if route.active else 'No'}")
        lines.append(f"  Next Hop: {route.next_hop}")

        # Include enriched next-hop information if available
        if route.next_hop_asn and route.next_hop_asn != "None":
            next_hop_info = f"AS{route.next_hop_asn}"
            if route.next_hop_org and route.next_hop_org != "None":
                next_hop_info += f" ({route.next_hop_org})"
            if route.next_hop_country and route.next_hop_country != "None":
                next_hop_info += f" [{route.next_hop_country}]"
            lines.append(f"  Next Hop Info: {next_hop_info}")

        lines.append(f"  AS Path: {' '.join(map(str, route.as_path))}")
        lines.append(f"  Source AS: AS{route.source_as}")
        lines.append("")

    return "\n".join(lines)


def format_enriched_traceroute_output(traceroute: TracerouteResult) -> str:
    """Format enriched traceroute result for display."""
    lines = []
    lines.append(f"Traceroute to {traceroute.target} from {traceroute.source}")
    lines.append(f"AS Path Summary: {traceroute.as_path_summary}")
    lines.append(f"Unique ASNs: {', '.join([f'AS{asn}' for asn in traceroute.unique_asns])}")
    lines.append("-" * 80)

    for hop in traceroute.hops:
        hop_line = f"{hop.hop_number:2d}. "

        if hop.is_timeout:
            hop_line += "* * * Request timed out"
        else:
            if hop.ip_address:
                hop_line += hop.ip_address
                if hop.hostname and hop.hostname != hop.ip_address:
                    hop_line += f" ({hop.hostname})"
            else:
                hop_line += "Unknown"

            # Add RTT information
            rtts = []
            for rtt in [hop.rtt1, hop.rtt2, hop.rtt3]:
                if rtt is not None:
                    rtts.append(f"{rtt:.2f} ms")
                else:
                    rtts.append("*")
            hop_line += f"  {' '.join(rtts)}"

            # Add enriched ASN information if available
            if hop.asn and hop.asn != "None":
                hop_line += f"  [{hop.asn_display}]"
                if hop.country and hop.country != "None":
                    hop_line += f" {hop.country}"

        lines.append(hop_line)

    return "\n".join(lines)


async def execute_with_enrichment(query, original_execute_func) -> t.Union[OutputDataModel, str]:
    """Execute query and enrich results with IP enrichment data."""
    # Execute the original query
    output = await original_execute_func(query)

    # If output is structured data, enrich it
    if isinstance(output, (BGPRouteTable, TracerouteResult)):
        enriched_output = await enrich_output_with_ip_enrichment(output)

        # Format for display if needed
        if isinstance(enriched_output, BGPRouteTable):
            return format_enriched_bgp_output(enriched_output)
        elif isinstance(enriched_output, TracerouteResult):
            return format_enriched_traceroute_output(enriched_output)

    return output
