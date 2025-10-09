"""Parse Juniper traceroute output to structured data."""

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


def parse_juniper_traceroute(
    output: t.Union[str, t.Sequence[str]], target: str, source: str
) -> "OutputDataModel":
    """Parse a Juniper traceroute text response."""
    result = None
    out_list = _normalize_output(output)

    _log = log.bind(plugin=TraceroutePluginJuniper.__name__)
    combined_output = "\n".join(out_list)

    # DEBUG: Log the raw output we're about to parse
    _log.debug(f"=== JUNIPER TRACEROUTE PLUGIN RAW INPUT ===")
    _log.debug(f"Target: {target}, Source: {source}")
    _log.debug(f"Output pieces: {len(out_list)}")
    _log.debug(f"Combined output length: {len(combined_output)}")
    _log.debug(f"First 500 chars: {repr(combined_output[:500])}")
    _log.debug(f"=== END PLUGIN RAW INPUT ===")

    try:
        result = JuniperTracerouteTable.parse_text(combined_output, target, source)
    except Exception as exc:
        _log.error(f"Failed to parse Juniper traceroute: {exc}")
        raise ParsingError(f"Failed to parse Juniper traceroute output: {exc}") from exc

    _log.debug(f"=== FINAL STRUCTURED TRACEROUTE RESULT ===")
    _log.debug(f"Successfully parsed {len(result.hops)} traceroute hops")
    _log.debug(f"Target: {target}, Source: {source}")
    for hop in result.hops:
        _log.debug(f"Hop {hop.hop_number}: {hop.ip_address or '*'} - RTT: {hop.rtt1 or 'timeout'}")
    _log.debug(f"Raw output length: {len(combined_output)} characters")
    _log.debug(f"=== END STRUCTURED RESULT ===")

    return result


class JuniperTracerouteTable(TracerouteResult):
    """Juniper traceroute table parser."""

    @classmethod
    def parse_text(cls, text: str, target: str, source: str) -> TracerouteResult:
        """Parse Juniper traceroute text output into structured data."""
        _log = log.bind(parser="JuniperTracerouteTable")

        _log.debug(f"=== RAW JUNIPER TRACEROUTE INPUT ===")
        _log.debug(f"Target: {target}, Source: {source}")
        _log.debug(f"Raw text length: {len(text)} characters")
        _log.debug(f"Raw text:\n{repr(text)}")
        _log.debug(f"=== END RAW INPUT ===")

        hops = []
        lines = text.strip().split("\n")

        _log.debug(f"Split into {len(lines)} lines")

        # Pattern for normal hop: " 1  102.218.156.197 (102.218.156.197)  0.928 ms  0.968 ms  0.677 ms"
        hop_pattern = re.compile(
            r"^\s*(\d+)\s+([^\s]+)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms(?:\s+(\d+(?:\.\d+)?)\s*ms)?(?:\s+(\d+(?:\.\d+)?)\s*ms)?"
        )

        # Pattern for timeout with IP: " 6  * 130.117.15.146 (130.117.15.146)  162.503 ms  162.773 ms"
        timeout_with_ip_pattern = re.compile(
            r"^\s*(\d+)\s+\*\s+([^\s]+)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms(?:\s+(\d+(?:\.\d+)?)\s*ms)?(?:\s+(\d+(?:\.\d+)?)\s*ms)?"
        )

        # Pattern for mixed timeout and IP: " 7  80.231.196.36 (80.231.196.36)  328.264 ms  328.938 ms *"
        mixed_timeout_pattern = re.compile(
            r"^\s*(\d+)\s+([^\s]+)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms(?:\s+(\d+(?:\.\d+)?)\s*ms)?\s+\*"
        )

        # Pattern for multipath: " 3  197.157.77.179 (197.157.77.179)  169.860 ms 41.78.188.48 (41.78.188.48)  185.519 ms  1006.603 ms"
        multipath_pattern = re.compile(
            r"^\s*(\d+)\s+([^\s]+)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms\s+([^\s]+)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms(?:\s+(\d+(?:\.\d+)?)\s*ms)?"
        )

        # Pattern for IPv6 multipath: "25  2001:41d0:0:50::7:100b (2001:41d0:0:50::7:100b)  460.762 ms 2001:41d0:0:50::7:1009 (2001:41d0:0:50::7:1009)  464.993 ms 2001:41d0:0:50::7:100f (2001:41d0:0:50::7:100f)  464.366 ms"
        ipv6_multipath_pattern = re.compile(
            r"^\s*(\d+)\s+([a-fA-F0-9:]+)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms\s+([a-fA-F0-9:]+)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms(?:\s+([a-fA-F0-9:]+)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms)?"
        )

        # Pattern for complete timeout: " 1  * * *"
        timeout_pattern = re.compile(r"^\s*(\d+)\s+\*\s*\*\s*\*")

        # Pattern for partial timeout at end: "10  * * 2001:978:3::12e (2001:978:3::12e)  200.936 ms"
        partial_timeout_pattern = re.compile(
            r"^\s*(\d+)\s+\*\s+\*\s+([^\s]+)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms"
        )

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            _log.debug(f"Line {i:2d}: {repr(line)}")

            if not line:
                i += 1
                continue

            # Skip header lines
            if (
                "traceroute to" in line.lower()
                or "traceroute6 to" in line.lower()
                or "hops max" in line.lower()
                or "byte packets" in line.lower()
            ):
                _log.debug(f"Line {i:2d}: SKIPPING HEADER")
                i += 1
                continue

            # Skip MPLS label lines
            if "MPLS Label=" in line:
                _log.debug(f"Line {i:2d}: SKIPPING MPLS LABEL")
                i += 1
                continue

            # Try to match complete timeout hop first
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
                        sent_count=3,
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
                i += 1
                continue

            # Try to match partial timeout: "10  * * 2001:978:3::12e (2001:978:3::12e)  200.936 ms"
            partial_timeout_match = partial_timeout_pattern.match(line)
            if partial_timeout_match:
                hop_number = int(partial_timeout_match.group(1))
                ip_address = partial_timeout_match.group(3)
                hostname = partial_timeout_match.group(2).strip()
                rtt1 = float(partial_timeout_match.group(4))

                _log.debug(
                    f"Line {i:2d}: PARTIAL TIMEOUT HOP - {hop_number}: * * {hostname} ({ip_address}) {rtt1}ms"
                )

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip_address,
                        display_ip=None,
                        hostname=hostname if hostname != ip_address else None,
                        rtt1=rtt1,
                        rtt2=None,
                        rtt3=None,
                        sent_count=3,
                        last_rtt=rtt1,
                        best_rtt=rtt1,
                        worst_rtt=rtt1,
                        loss_pct=66,  # 2 out of 3 packets lost
                        # BGP enrichment fields
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                i += 1
                continue

            # Try to match IPv6 multipath
            ipv6_multipath_match = ipv6_multipath_pattern.match(line)
            if ipv6_multipath_match:
                hop_number = int(ipv6_multipath_match.group(1))
                ip1 = ipv6_multipath_match.group(3)
                hostname1 = ipv6_multipath_match.group(2).strip()
                rtt1 = float(ipv6_multipath_match.group(4))
                ip2 = ipv6_multipath_match.group(6)
                hostname2 = ipv6_multipath_match.group(5).strip()
                rtt2 = float(ipv6_multipath_match.group(7))

                rtt3 = None
                if ipv6_multipath_match.group(10):  # Third IP/RTT pair
                    rtt3 = float(ipv6_multipath_match.group(10))

                _log.debug(
                    f"Line {i:2d}: IPv6 MULTIPATH HOP - {hop_number}: {hostname1}/{hostname2} ({ip1}/{ip2})"
                )

                display_hostname = f"{hostname1} / {hostname2}"
                if ipv6_multipath_match.group(8):  # Third hostname
                    hostname3 = ipv6_multipath_match.group(8).strip()
                    display_hostname += f" / {hostname3}"

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
                        # BGP enrichment fields
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                i += 1
                continue

            # Try to match multipath IPv4
            multipath_match = multipath_pattern.match(line)
            if multipath_match:
                hop_number = int(multipath_match.group(1))
                hostname1 = multipath_match.group(2).strip()
                ip1 = multipath_match.group(3)
                rtt1 = float(multipath_match.group(4))
                hostname2 = multipath_match.group(5).strip()
                ip2 = multipath_match.group(6)
                rtt2 = float(multipath_match.group(7))
                rtt3 = float(multipath_match.group(8)) if multipath_match.group(8) else None

                _log.debug(
                    f"Line {i:2d}: MULTIPATH HOP - {hop_number}: {hostname1}/{hostname2} ({ip1}/{ip2})"
                )

                display_hostname = f"{hostname1} / {hostname2}"
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
                        # BGP enrichment fields
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                i += 1
                continue

            # Try to match timeout with IP: " 6  * 130.117.15.146 (130.117.15.146)  162.503 ms  162.773 ms"
            timeout_with_ip_match = timeout_with_ip_pattern.match(line)
            if timeout_with_ip_match:
                hop_number = int(timeout_with_ip_match.group(1))
                hostname = timeout_with_ip_match.group(2).strip()
                ip_address = timeout_with_ip_match.group(3)
                rtt1 = float(timeout_with_ip_match.group(4))
                rtt2 = (
                    float(timeout_with_ip_match.group(5))
                    if timeout_with_ip_match.group(5)
                    else None
                )
                rtt3 = (
                    float(timeout_with_ip_match.group(6))
                    if timeout_with_ip_match.group(6)
                    else None
                )

                _log.debug(
                    f"Line {i:2d}: TIMEOUT WITH IP - {hop_number}: * {hostname} ({ip_address})"
                )

                rtts = [x for x in [rtt1, rtt2, rtt3] if x is not None]
                loss_pct = int((3 - len(rtts)) / 3 * 100) if len(rtts) > 0 else 100

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip_address,
                        display_ip=None,
                        hostname=hostname if hostname != ip_address else None,
                        rtt1=rtt1,
                        rtt2=rtt2,
                        rtt3=rtt3,
                        sent_count=3,
                        last_rtt=rtts[-1] if rtts else None,
                        best_rtt=min(rtts) if rtts else None,
                        worst_rtt=max(rtts) if rtts else None,
                        loss_pct=loss_pct,
                        # BGP enrichment fields
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                i += 1
                continue

            # Try to match mixed timeout: " 7  80.231.196.36 (80.231.196.36)  328.264 ms  328.938 ms *"
            mixed_timeout_match = mixed_timeout_pattern.match(line)
            if mixed_timeout_match:
                hop_number = int(mixed_timeout_match.group(1))
                hostname = mixed_timeout_match.group(2).strip()
                ip_address = mixed_timeout_match.group(3)
                rtt1 = float(mixed_timeout_match.group(4))
                rtt2 = float(mixed_timeout_match.group(5)) if mixed_timeout_match.group(5) else None

                _log.debug(
                    f"Line {i:2d}: MIXED TIMEOUT - {hop_number}: {hostname} ({ip_address}) with *"
                )

                rtts = [x for x in [rtt1, rtt2] if x is not None]
                loss_pct = int((3 - len(rtts)) / 3 * 100)

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip_address,
                        display_ip=None,
                        hostname=hostname if hostname != ip_address else None,
                        rtt1=rtt1,
                        rtt2=rtt2,
                        rtt3=None,
                        sent_count=3,
                        last_rtt=rtts[-1] if rtts else None,
                        best_rtt=min(rtts) if rtts else None,
                        worst_rtt=max(rtts) if rtts else None,
                        loss_pct=loss_pct,
                        # BGP enrichment fields
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                i += 1
                continue

            # Try to match normal hop
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
                        # BGP enrichment fields
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                i += 1
                continue

            _log.debug(f"Line {i:2d}: UNMATCHED - skipping")
            i += 1

        _log.debug(f"Before cleanup: {len(hops)} hops")

        # Clean up consecutive timeout hops at the end
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

        _log.info(f"Parsed {len(hops)} hops from Juniper traceroute")

        # Extract packet size and max hops from header if available
        max_hops = 30  # Default for Juniper
        packet_size = 52  # Default from your examples

        for line in text.split("\n"):
            if "hops max" in line and "byte packets" in line:
                # Example: "traceroute to 51.161.209.134 (51.161.209.134) from 196.201.112.49, 30 hops max, 52 byte packets"
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


class TraceroutePluginJuniper(OutputPlugin):
    """Parse Juniper traceroute output."""

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: t.Sequence[str] = ("juniper", "juniper_junos")
    directives: t.Sequence[str] = ("__hyperglass_juniper_traceroute__",)
    common: bool = False

    def process(self, output: "OutputType", query: "Query") -> "OutputType":
        """Process Juniper traceroute output."""
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

        return parse_juniper_traceroute(
            output=output,
            target=target,
            source=source,
        )
