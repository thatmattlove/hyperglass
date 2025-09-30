"""Parse FRR traceroute output to structured data."""

# Standard Library
import re
import typing as t

# Third Party
from pydantic import PrivateAttr

# Project
from hyperglass.log import log
from hyperglass.exceptions.private import ParsingError
from hyperglass.models.data.traceroute import TracerouteResult, TracerouteHop
from hyperglass.state import use_state

# Local
from .._output import OutputPlugin

if t.TYPE_CHECKING:
    from hyperglass.models.data import OutputDataModel
    from hyperglass.models.api.query import Query
    from .._output import OutputType


def _normalize_output(output: t.Union[str, t.Sequence[str]]) -> t.List[str]:
    """Ensure the output is a list of strings."""
    if isinstance(output, str):
        return [output]
    return list(output)


def parse_frr_traceroute(
    output: t.Union[str, t.Sequence[str]], target: str, source: str
) -> "OutputDataModel":
    """Parse an FRR traceroute text response."""
    result = None
    out_list = _normalize_output(output)

    _log = log.bind(plugin=TraceroutePluginFrr.__name__)
    combined_output = "\n".join(out_list)

    # DEBUG: Log the raw output we're about to parse
    _log.debug(f"=== FRR TRACEROUTE PLUGIN RAW INPUT ===")
    _log.debug(f"Target: {target}, Source: {source}")
    _log.debug(f"Output pieces: {len(out_list)}")
    _log.debug(f"Combined output length: {len(combined_output)}")
    _log.debug(f"First 500 chars: {repr(combined_output[:500])}")
    _log.debug(f"=== END PLUGIN RAW INPUT ===")

    try:
        result = FrrTracerouteTable.parse_text(combined_output, target, source)
    except Exception as exc:
        _log.error(f"Failed to parse FRR traceroute: {exc}")
        raise ParsingError(f"Failed to parse FRR traceroute output: {exc}") from exc

    _log.debug(f"=== FINAL STRUCTURED TRACEROUTE RESULT ===")
    _log.debug(f"Successfully parsed {len(result.hops)} traceroute hops")
    _log.debug(f"Target: {target}, Source: {source}")
    for hop in result.hops:
        _log.debug(f"Hop {hop.hop_number}: {hop.ip_address or '*'} - RTT: {hop.rtt1 or 'timeout'}")
    _log.debug(f"Raw output length: {len(combined_output)} characters")
    _log.debug(f"=== END STRUCTURED RESULT ===")

    return result


class FrrTracerouteTable(TracerouteResult):
    """FRR traceroute table parser."""

    @classmethod
    def parse_text(cls, text: str, target: str, source: str) -> TracerouteResult:
        """Parse FRR traceroute text output into structured data."""
        _log = log.bind(parser="FrrTracerouteTable")

        _log.debug(f"=== RAW FRR TRACEROUTE INPUT ===")
        _log.debug(f"Target: {target}, Source: {source}")
        _log.debug(f"Raw text length: {len(text)} characters")
        _log.debug(f"Raw text:\n{repr(text)}")
        _log.debug(f"=== END RAW INPUT ===")

        hops = []
        lines = text.strip().split("\n")

        _log.debug(f"Split into {len(lines)} lines")

        # Pattern for normal hop: " 1  bdr2.std.douala-ix.net (196.49.84.34)  0.520 ms  0.451 ms  0.418 ms"
        hop_pattern = re.compile(
            r"^\s*(\d+)\s+(.+?)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms(?:\s+(\d+(?:\.\d+)?)\s*ms)?(?:\s+(\d+(?:\.\d+)?)\s*ms)?"
        )

        # Pattern for timeout hop: " 3  * * *"
        timeout_pattern = re.compile(r"^\s*(\d+)\s+\*\s*\*\s*\*")

        # Pattern for partial timeout: " 7  port-channel4.core4.mrs1.he.net (184.105.81.30)  132.624 ms  132.589 ms *"
        partial_timeout_pattern = re.compile(
            r"^\s*(\d+)\s+(.+?)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms(?:\s+(\d+(?:\.\d+)?)\s*ms)?\s+\*"
        )

        # Pattern for IP-only hop: "15  72.251.0.8 (72.251.0.8)  360.370 ms  352.170 ms  354.132 ms"
        ip_only_pattern = re.compile(
            r"^\s*(\d+)\s+([0-9a-fA-F:.]+)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms(?:\s+(\d+(?:\.\d+)?)\s*ms)?(?:\s+(\d+(?:\.\d+)?)\s*ms)?"
        )

        # Complex multi-IP patterns for load balancing scenarios
        # Pattern 1: "18  * 2001:41d0:0:50::7:1009 (2001:41d0:0:50::7:1009)  353.548 ms  351.516 ms"
        partial_multi_pattern = re.compile(
            r"^\s*(\d+)\s+\*\s+(.+?)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms(?:\s+(\d+(?:\.\d+)?)\s*ms)?"
        )

        # Pattern 2: "12  2001:41d0:aaaa:100::3 (2001:41d0:aaaa:100::3)  274.418 ms 2001:41d0:aaaa:100::5 (2001:41d0:aaaa:100::5)  269.972 ms  282.653 ms"
        dual_ip_pattern = re.compile(
            r"^\s*(\d+)\s+(.+?)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms\s+(.+?)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms(?:\s+(\d+(?:\.\d+)?)\s*ms)?"
        )

        # Pattern 3: More complex multi-IP lines (3 or more IPs)
        # "19  2001:41d0:0:50::3:211b (2001:41d0:0:50::3:211b)  351.213 ms 2001:41d0:0:50::7:100f (2001:41d0:0:50::7:100f)  351.090 ms 2001:41d0:0:50::7:100b (2001:41d0:0:50::7:100b)  351.282 ms"
        multi_ip_pattern = re.compile(
            r"^\s*(\d+)\s+(.+?)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms\s+(.+?)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms\s+(.+?)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms"
        )

        for i, line in enumerate(lines):
            line = line.strip()
            _log.debug(f"Line {i:2d}: {repr(line)}")

            if not line:
                continue

            # Skip header lines
            if (
                "traceroute to" in line.lower()
                or "hops max" in line.lower()
                or "byte packets" in line.lower()
            ):
                _log.debug(f"Line {i:2d}: SKIPPING HEADER")
                continue

            # Try to match timeout hop first
            timeout_match = timeout_pattern.match(line)
            if timeout_match:
                hop_number = int(timeout_match.group(1))

                _log.debug(f"Line {i:2d}: TIMEOUT HOP - {hop_number}: * * *")

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=None,
                        display_ip=None,
                        hostname=None,
                        rtt1=None,
                        rtt2=None,
                        rtt3=None,
                        sent_count=3,  # FRR sends 3 pings per hop
                        last_rtt=None,
                        best_rtt=None,
                        worst_rtt=None,
                        loss_pct=100,  # 100% loss for timeout
                        # BGP enrichment fields (all None for timeout)
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                continue

            # Try to match multi-IP pattern (3 IPs)
            multi_match = multi_ip_pattern.match(line)
            if multi_match:
                hop_number = int(multi_match.group(1))
                hostname1 = multi_match.group(2).strip()
                ip1 = multi_match.group(3)
                rtt1 = float(multi_match.group(4))
                hostname2 = multi_match.group(5).strip()
                ip2 = multi_match.group(6)
                rtt2 = float(multi_match.group(7))
                hostname3 = multi_match.group(8).strip()
                ip3 = multi_match.group(9)
                rtt3 = float(multi_match.group(10))

                _log.debug(f"Line {i:2d}: MULTI-IP HOP (3 IPs) - {hop_number}: {ip1}, {ip2}, {ip3}")

                # Use the first IP as primary, combine hostnames
                display_hostname = f"{hostname1} / {hostname2} / {hostname3}"
                if hostname1 == ip1:
                    display_hostname = None  # All IP-only

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip1,
                        display_ip=None,
                        hostname=display_hostname,
                        rtt1=rtt1,
                        rtt2=rtt2,
                        rtt3=rtt3,
                        sent_count=3,
                        last_rtt=rtt3,
                        best_rtt=min(rtt1, rtt2, rtt3),
                        worst_rtt=max(rtt1, rtt2, rtt3),
                        loss_pct=0,  # No loss if we got responses
                        # BGP enrichment fields (will be populated by enrichment plugin)
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                continue

            # Try to match dual-IP pattern
            dual_match = dual_ip_pattern.match(line)
            if dual_match:
                hop_number = int(dual_match.group(1))
                hostname1 = dual_match.group(2).strip()
                ip1 = dual_match.group(3)
                rtt1 = float(dual_match.group(4))
                hostname2 = dual_match.group(5).strip()
                ip2 = dual_match.group(6)
                rtt2 = float(dual_match.group(7))
                rtt3 = float(dual_match.group(8)) if dual_match.group(8) else None

                _log.debug(f"Line {i:2d}: DUAL-IP HOP - {hop_number}: {ip1} and {ip2}")

                # Use the first IP as primary, combine hostnames
                display_hostname = f"{hostname1} / {hostname2}"
                if hostname1 == ip1:
                    display_hostname = None  # Both IP-only

                rtts = [x for x in [rtt1, rtt2, rtt3] if x is not None]

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip1,
                        display_ip=None,
                        hostname=display_hostname,
                        rtt1=rtt1,
                        rtt2=rtt2,
                        rtt3=rtt3,
                        sent_count=len(rtts),
                        last_rtt=rtts[-1] if rtts else None,
                        best_rtt=min(rtts) if rtts else None,
                        worst_rtt=max(rtts) if rtts else None,
                        loss_pct=0,  # No loss if we got responses
                        # BGP enrichment fields (will be populated by enrichment plugin)
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                continue

            # Try to match partial multi pattern (* hostname)
            partial_multi_match = partial_multi_pattern.match(line)
            if partial_multi_match:
                hop_number = int(partial_multi_match.group(1))
                hostname = partial_multi_match.group(2).strip()
                ip_address = partial_multi_match.group(3)
                rtt1 = float(partial_multi_match.group(4))
                rtt2 = float(partial_multi_match.group(5)) if partial_multi_match.group(5) else None

                _log.debug(
                    f"Line {i:2d}: PARTIAL-MULTI HOP - {hop_number}: * {hostname} ({ip_address})"
                )

                rtts = [x for x in [rtt1, rtt2] if x is not None]

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip_address,
                        display_ip=None,
                        hostname=hostname if hostname != ip_address else None,
                        rtt1=rtt1,
                        rtt2=rtt2,
                        rtt3=None,
                        sent_count=3,  # Still sent 3, but one timed out
                        last_rtt=rtts[-1] if rtts else None,
                        best_rtt=min(rtts) if rtts else None,
                        worst_rtt=max(rtts) if rtts else None,
                        loss_pct=33.33,  # 1 out of 3 packets lost
                        # BGP enrichment fields (will be populated by enrichment plugin)
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                continue

            # Try to match partial timeout (hostname with one *)
            partial_timeout_match = partial_timeout_pattern.match(line)
            if partial_timeout_match:
                hop_number = int(partial_timeout_match.group(1))
                hostname = partial_timeout_match.group(2).strip()
                ip_address = partial_timeout_match.group(3)
                rtt1 = float(partial_timeout_match.group(4))
                rtt2 = (
                    float(partial_timeout_match.group(5))
                    if partial_timeout_match.group(5)
                    else None
                )

                _log.debug(
                    f"Line {i:2d}: PARTIAL-TIMEOUT HOP - {hop_number}: {hostname} ({ip_address}) with timeout"
                )

                rtts = [x for x in [rtt1, rtt2] if x is not None]

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip_address,
                        display_ip=None,
                        hostname=hostname if hostname != ip_address else None,
                        rtt1=rtt1,
                        rtt2=rtt2,
                        rtt3=None,
                        sent_count=3,  # Still sent 3, but one timed out
                        last_rtt=rtts[-1] if rtts else None,
                        best_rtt=min(rtts) if rtts else None,
                        worst_rtt=max(rtts) if rtts else None,
                        loss_pct=33.33,  # 1 out of 3 packets lost
                        # BGP enrichment fields (will be populated by enrichment plugin)
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                continue

            # Try to match normal hop with hostname
            hop_match = hop_pattern.match(line)
            if hop_match:
                hop_number = int(hop_match.group(1))
                hostname = hop_match.group(2).strip()
                ip_address = hop_match.group(3)
                rtt1 = float(hop_match.group(4))
                rtt2 = float(hop_match.group(5)) if hop_match.group(5) else None
                rtt3 = float(hop_match.group(6)) if hop_match.group(6) else None

                _log.debug(
                    f"Line {i:2d}: NORMAL HOP - {hop_number}: {hostname} ({ip_address}) RTTs: {rtt1}, {rtt2}, {rtt3}"
                )

                rtts = [x for x in [rtt1, rtt2, rtt3] if x is not None]

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip_address,
                        display_ip=None,
                        hostname=hostname if hostname != ip_address else None,
                        rtt1=rtt1,
                        rtt2=rtt2,
                        rtt3=rtt3,
                        sent_count=len(rtts),
                        last_rtt=rtts[-1] if rtts else None,
                        best_rtt=min(rtts) if rtts else None,
                        worst_rtt=max(rtts) if rtts else None,
                        loss_pct=0,  # No loss if we got a response
                        # BGP enrichment fields (will be populated by enrichment plugin)
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                continue

            # Try to match IP-only hop (no hostname)
            ip_match = ip_only_pattern.match(line)
            if ip_match:
                hop_number = int(ip_match.group(1))
                ip_display = ip_match.group(2).strip()  # The IP shown before parentheses
                ip_address = ip_match.group(3)  # The IP in parentheses
                rtt1 = float(ip_match.group(4))
                rtt2 = float(ip_match.group(5)) if ip_match.group(5) else None
                rtt3 = float(ip_match.group(6)) if ip_match.group(6) else None

                _log.debug(
                    f"Line {i:2d}: IP-ONLY HOP - {hop_number}: {ip_address} RTTs: {rtt1}, {rtt2}, {rtt3}"
                )

                rtts = [x for x in [rtt1, rtt2, rtt3] if x is not None]

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip_address,
                        display_ip=None,
                        hostname=None,  # No hostname for IP-only hops
                        rtt1=rtt1,
                        rtt2=rtt2,
                        rtt3=rtt3,
                        sent_count=len(rtts),
                        last_rtt=rtts[-1] if rtts else None,
                        best_rtt=min(rtts) if rtts else None,
                        worst_rtt=max(rtts) if rtts else None,
                        loss_pct=0,  # No loss if we got a response
                        # BGP enrichment fields (will be populated by enrichment plugin)
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                continue

            _log.debug(f"Line {i:2d}: UNMATCHED - skipping")

        _log.debug(f"Before cleanup: {len(hops)} hops")

        # Clean up consecutive timeout hops at the end
        # Keep only the first few timeouts, remove excessive trailing timeouts
        if len(hops) > 5:
            # Find the last non-timeout hop
            last_real_hop = -1
            for i in range(len(hops) - 1, -1, -1):
                if not hops[i].is_timeout:
                    last_real_hop = i
                    break

            if last_real_hop >= 0:
                # Keep at most 3 timeout hops after the last real hop
                max_timeouts = 3
                timeout_count = 0
                cleaned_hops = hops[: last_real_hop + 1]  # Keep all hops up to last real hop

                for hop in hops[last_real_hop + 1 :]:
                    if hop.is_timeout:
                        timeout_count += 1
                        if timeout_count <= max_timeouts:
                            cleaned_hops.append(hop)
                        else:
                            _log.debug(f"Removing excessive timeout hop {hop.hop_number}")
                    else:
                        # If we find another real hop after timeouts, keep it
                        cleaned_hops.append(hop)
                        timeout_count = 0

                hops = cleaned_hops

        _log.debug(f"After cleanup: {len(hops)} hops")

        for hop in hops:
            if hop.is_timeout:
                _log.debug(f"Final hop {hop.hop_number}: * (timeout)")
            else:
                _log.debug(
                    f"Final hop {hop.hop_number}: {hop.ip_address} ({hop.hostname or 'no-hostname'}) - RTTs: {hop.rtt1}/{hop.rtt2}/{hop.rtt3}"
                )

        _log.info(f"Parsed {len(hops)} hops from FRR traceroute")

        # Extract packet size and max hops from header if available
        max_hops = 30  # Default from your examples
        packet_size = 60  # Default from your examples (IPv4)

        for line in text.split("\n"):
            if "hops max" in line and "byte packets" in line:
                # Example: "traceroute to syd.proof.ovh.net (51.161.209.134), 30 hops max, 60 byte packets"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "hops":
                        try:
                            max_hops = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass
                    elif part == "byte":
                        try:
                            packet_size = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass
                break

        return TracerouteResult(
            target=target,
            source=source,
            hops=hops,
            max_hops=max_hops,
            packet_size=packet_size,
            raw_output=text,
            asn_organizations={},
        )


class TraceroutePluginFrr(OutputPlugin):
    """Parse FRR traceroute output."""

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: t.Sequence[str] = ("frr",)
    directives: t.Sequence[str] = ("__hyperglass_frr_traceroute__",)
    common: bool = False

    def process(self, output: "OutputType", query: "Query") -> "OutputType":
        """Process FRR traceroute output."""
        # Extract target and source with fallbacks
        target = str(query.query_target) if query.query_target else "unknown"
        source = "unknown"

        if hasattr(query, "device") and query.device:
            source = getattr(query.device, "display_name", None) or getattr(
                query.device, "name", "unknown"
            )

        device = getattr(query, "device", None)
        if device is not None:
            if not getattr(device, "structured_output", False):
                return output
            try:
                _params = use_state("params")
            except Exception:
                _params = None
            if (
                _params
                and getattr(_params, "structured", None)
                and getattr(_params.structured, "enable_for_traceroute", None) is False
            ):
                return output
        else:
            try:
                params = use_state("params")
            except Exception:
                params = None
            if not (params and getattr(params, "structured", None)):
                return output
            if getattr(params.structured, "enable_for_traceroute", None) is False:
                return output

        return parse_frr_traceroute(
            output=output,
            target=target,
            source=source,
        )
