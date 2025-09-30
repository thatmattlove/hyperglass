"""Parse Arista traceroute output to structured data."""

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


def parse_arista_traceroute(
    output: t.Union[str, t.Sequence[str]], target: str, source: str
) -> "OutputDataModel":
    """Parse an Arista traceroute text response."""
    result = None
    out_list = _normalize_output(output)

    _log = log.bind(plugin=TraceroutePluginArista.__name__)
    combined_output = "\n".join(out_list)

    # DEBUG: Log the raw output we're about to parse
    _log.debug(f"=== ARISTA TRACEROUTE PLUGIN RAW INPUT ===")
    _log.debug(f"Target: {target}, Source: {source}")
    _log.debug(f"Output pieces: {len(out_list)}")
    _log.debug(f"Combined output length: {len(combined_output)}")
    _log.debug(f"First 500 chars: {repr(combined_output[:500])}")
    _log.debug(f"=== END PLUGIN RAW INPUT ===")

    try:
        result = AristaTracerouteTable.parse_text(combined_output, target, source)
    except Exception as exc:
        _log.error(f"Failed to parse Arista traceroute: {exc}")
        raise ParsingError(f"Failed to parse Arista traceroute output: {exc}") from exc

    _log.debug(f"=== FINAL STRUCTURED TRACEROUTE RESULT ===")
    _log.debug(f"Successfully parsed {len(result.hops)} traceroute hops")
    _log.debug(f"Target: {target}, Source: {source}")
    for hop in result.hops:
        _log.debug(f"Hop {hop.hop_number}: {hop.ip_address or '*'} - RTT: {hop.rtt1 or 'timeout'}")
    _log.debug(f"Raw output length: {len(combined_output)} characters")
    _log.debug(f"=== END STRUCTURED RESULT ===")

    return result


class AristaTracerouteTable(TracerouteResult):
    """Arista traceroute table parser."""

    @classmethod
    def parse_text(cls, text: str, target: str, source: str) -> TracerouteResult:
        """Parse Arista traceroute text output into structured data."""
        _log = log.bind(parser="AristaTracerouteTable")

        _log.debug(f"=== RAW ARISTA TRACEROUTE INPUT ===")
        _log.debug(f"Target: {target}, Source: {source}")
        _log.debug(f"Raw text length: {len(text)} characters")
        _log.debug(f"Raw text:\n{repr(text)}")
        _log.debug(f"=== END RAW INPUT ===")

        hops = []
        lines = text.strip().split("\n")

        _log.debug(f"Split into {len(lines)} lines")

        # Pattern for normal hop: " 1    er03-ter.jhb.as37739.net (102.209.241.6)    0.285 ms    0.177 ms    0.137 ms"
        # Also handles IPv6: " 1    2001:43f8:6d0::10:3 (2001:43f8:6d0::10:3)    19.460 ms    19.416 ms    19.353 ms"
        hop_pattern = re.compile(
            r"^\s*(\d+)\s+(.+?)\s+\(([^)]+)\)(?:\s+<[^>]+>)?\s+(\d+(?:\.\d+)?)\s*ms(?:\s+(\d+(?:\.\d+)?)\s*ms)?(?:\s+(\d+(?:\.\d+)?)\s*ms)?"
        )

        # Pattern for MPLS hop with labels: " 2  41.78.188.48 (41.78.188.48) <MPLS:L=116443,E=0,S=1,T=1>  1653.906 ms"
        mpls_hop_pattern = re.compile(
            r"^\s*(\d+)\s+(.+?)\s+\(([^)]+)\)\s+<MPLS:[^>]+>\s+(\d+(?:\.\d+)?)\s*ms(?:\s+(\d+(?:\.\d+)?)\s*ms)?(?:\s+(.+?)\s+\(([^)]+)\)\s+<MPLS:[^>]+>\s+(\d+(?:\.\d+)?)\s*ms)?"
        )

        # Pattern for complex multipath with mixed timeouts and IPs:
        # "10  ae22.cr11-lon2.ip6.gtt.net (2001:668:0:3:ffff:1:0:3471)  201.963 ms be8443.ccr41.lon13.atlas.cogentco.com (2001:550:0:1000::9a36:3859)  184.724 ms *"
        complex_multipath_pattern = re.compile(
            r"^\s*(\d+)\s+(.+?)\s+\(([^)]+)\)(?:\s+<[^>]+>)?\s+(\d+(?:\.\d+)?)\s*ms\s+(.+?)\s+\(([^)]+)\)(?:\s+<[^>]+>)?\s+(\d+(?:\.\d+)?)\s*ms(?:\s+\*|\s+(.+?)\s+\(([^)]+)\)(?:\s+<[^>]+>)?\s+(\d+(?:\.\d+)?)\s*ms)?"
        )

        # Pattern for partial timeout multipath: " 8  * * 2c0f:fa90:0:8::5 (2c0f:fa90:0:8::5)  179.449 ms"
        partial_timeout_pattern = re.compile(
            r"^\s*(\d+)\s+\*\s+\*\s+(.+?)\s+\(([^)]+)\)(?:\s+<[^>]+>)?\s+(\d+(?:\.\d+)?)\s*ms"
        )

        # Pattern for mixed timeout start: " 9  ae22.cr11-lon2.ip6.gtt.net (2001:668:0:3:ffff:1:0:3471)  201.979 ms * 2c0f:fa90:0:8::5 (2c0f:fa90:0:8::5)  179.438 ms"
        mixed_timeout_start_pattern = re.compile(
            r"^\s*(\d+)\s+(.+?)\s+\(([^)]+)\)(?:\s+<[^>]+>)?\s+(\d+(?:\.\d+)?)\s*ms\s+\*\s+(.+?)\s+\(([^)]+)\)(?:\s+<[^>]+>)?\s+(\d+(?:\.\d+)?)\s*ms"
        )

        # Pattern for triple multipath IPv6: "30  2001:41d0:0:50::b:66 (2001:41d0:0:50::b:66)  442.036 ms 2402:1f00:8201:586:: (2402:1f00:8201:586::)  456.999 ms 2001:41d0:0:50::b:66 (2001:41d0:0:50::b:66)  441.399 ms"
        triple_multipath_pattern = re.compile(
            r"^\s*(\d+)\s+(.+?)\s+\(([^)]+)\)(?:\s+<[^>]+>)?\s+(\d+(?:\.\d+)?)\s*ms\s+(.+?)\s+\(([^)]+)\)(?:\s+<[^>]+>)?\s+(\d+(?:\.\d+)?)\s*ms\s+(.+?)\s+\(([^)]+)\)(?:\s+<[^>]+>)?\s+(\d+(?:\.\d+)?)\s*ms"
        )

        # Pattern for multiple IPs in one hop (load balancing):
        # " 2    po204.asw02.jnb1.tfbnw.net (2620:0:1cff:dead:beef::5316)    0.249 ms    0.234 ms po204.asw04.jnb1.tfbnw.net (2620:0:1cff:dead:beef::5524)    0.244 ms"
        multi_hop_pattern = re.compile(
            r"^\s*(\d+)\s+(.+?)\s+\(([^)]+)\)(?:\s+<[^>]+>)?\s+(\d+(?:\.\d+)?)\s*ms(?:\s+(\d+(?:\.\d+)?)\s*ms)?\s+(.+?)\s+\(([^)]+)\)(?:\s+<[^>]+>)?\s+(\d+(?:\.\d+)?)\s*ms"
        )

        # Pattern for timeout hop: " 6    * * *"
        timeout_pattern = re.compile(r"^\s*(\d+)\s+\*\s*\*\s*\*")

        # Pattern for single IP without hostname: "12    72.251.0.8 (72.251.0.8)    421.861 ms    421.788 ms    419.821 ms"
        ip_only_pattern = re.compile(
            r"^\s*(\d+)\s+([0-9a-fA-F:.]+)\s+\(([^)]+)\)\s+(\d+(?:\.\d+)?)\s*ms(?:\s+(\d+(?:\.\d+)?)\s*ms)?(?:\s+(\d+(?:\.\d+)?)\s*ms)?"
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
                        sent_count=3,  # Arista sends 3 pings per hop
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

            # Try to match partial timeout: " 8  * * 2c0f:fa90:0:8::5 (2c0f:fa90:0:8::5)  179.449 ms"
            partial_timeout_match = partial_timeout_pattern.match(line)
            if partial_timeout_match:
                hop_number = int(partial_timeout_match.group(1))
                hostname = partial_timeout_match.group(2).strip()
                ip_address = partial_timeout_match.group(3)
                rtt1 = float(partial_timeout_match.group(4))

                _log.debug(
                    f"Line {i:2d}: PARTIAL TIMEOUT - {hop_number}: * * {hostname} ({ip_address}) {rtt1}ms"
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
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                continue

            # Try to match triple multipath IPv6
            triple_multipath_match = triple_multipath_pattern.match(line)
            if triple_multipath_match:
                hop_number = int(triple_multipath_match.group(1))
                hostname1 = triple_multipath_match.group(2).strip()
                ip1 = triple_multipath_match.group(3)
                rtt1 = float(triple_multipath_match.group(4))
                hostname2 = triple_multipath_match.group(5).strip()
                ip2 = triple_multipath_match.group(6)
                rtt2 = float(triple_multipath_match.group(7))
                hostname3 = triple_multipath_match.group(8).strip()
                ip3 = triple_multipath_match.group(9)
                rtt3 = float(triple_multipath_match.group(10))

                _log.debug(
                    f"Line {i:2d}: TRIPLE MULTIPATH - {hop_number}: {hostname1}/{hostname2}/{hostname3}"
                )

                display_hostname = f"{hostname1} / {hostname2} / {hostname3}"

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
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                continue

            # Try to match complex multipath with mixed timeouts
            complex_multipath_match = complex_multipath_pattern.match(line)
            if complex_multipath_match:
                hop_number = int(complex_multipath_match.group(1))
                hostname1 = complex_multipath_match.group(2).strip()
                ip1 = complex_multipath_match.group(3)
                rtt1 = float(complex_multipath_match.group(4))
                hostname2 = complex_multipath_match.group(5).strip()
                ip2 = complex_multipath_match.group(6)
                rtt2 = float(complex_multipath_match.group(7))

                # Check for third IP or timeout
                rtt3 = None
                hostname3 = None
                has_third = complex_multipath_match.group(8) is not None
                if has_third:
                    hostname3 = complex_multipath_match.group(8).strip()
                    rtt3 = float(complex_multipath_match.group(10))

                _log.debug(
                    f"Line {i:2d}: COMPLEX MULTIPATH - {hop_number}: {hostname1}/{hostname2}{('/' + hostname3) if hostname3 else ''}"
                )

                display_hostname = f"{hostname1} / {hostname2}"
                if hostname3:
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
                        loss_pct=int((3 - len(rtts)) / 3 * 100),
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                continue

            # Try to match mixed timeout with start response
            mixed_timeout_start_match = mixed_timeout_start_pattern.match(line)
            if mixed_timeout_start_match:
                hop_number = int(mixed_timeout_start_match.group(1))
                hostname1 = mixed_timeout_start_match.group(2).strip()
                ip1 = mixed_timeout_start_match.group(3)
                rtt1 = float(mixed_timeout_start_match.group(4))
                hostname2 = mixed_timeout_start_match.group(5).strip()
                ip2 = mixed_timeout_start_match.group(6)
                rtt2 = float(mixed_timeout_start_match.group(7))

                _log.debug(
                    f"Line {i:2d}: MIXED TIMEOUT START - {hop_number}: {hostname1} * {hostname2}"
                )

                display_hostname = f"{hostname1} / * / {hostname2}"

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip1,
                        display_ip=None,
                        hostname=display_hostname,
                        rtt1=rtt1,
                        rtt2=None,  # Middle packet timed out
                        rtt3=rtt2,
                        sent_count=3,
                        last_rtt=rtt2,
                        best_rtt=min(rtt1, rtt2),
                        worst_rtt=max(rtt1, rtt2),
                        loss_pct=33,  # 1 out of 3 packets lost
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                continue

            # Try to match MPLS hop
            mpls_hop_match = mpls_hop_pattern.match(line)
            if mpls_hop_match:
                hop_number = int(mpls_hop_match.group(1))
                hostname1 = mpls_hop_match.group(2).strip()
                ip1 = mpls_hop_match.group(3)
                rtt1 = float(mpls_hop_match.group(4))
                rtt2 = float(mpls_hop_match.group(5)) if mpls_hop_match.group(5) else None

                # Check for second MPLS hop in same line
                hostname2 = None
                ip2 = None
                rtt3 = None
                if mpls_hop_match.group(6):  # Second hostname exists
                    hostname2 = mpls_hop_match.group(6).strip()
                    ip2 = mpls_hop_match.group(7)
                    rtt3 = float(mpls_hop_match.group(8))

                _log.debug(
                    f"Line {i:2d}: MPLS HOP - {hop_number}: {hostname1} (MPLS){(' + ' + hostname2) if hostname2 else ''}"
                )

                display_hostname = hostname1
                if hostname2:
                    display_hostname += f" / {hostname2}"

                rtts = [x for x in [rtt1, rtt2, rtt3] if x is not None]

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip1,
                        display_ip=None,
                        hostname=display_hostname if display_hostname != ip1 else None,
                        rtt1=rtt1,
                        rtt2=rtt2,
                        rtt3=rtt3,
                        sent_count=len(rtts),
                        last_rtt=rtts[-1] if rtts else None,
                        best_rtt=min(rtts) if rtts else None,
                        worst_rtt=max(rtts) if rtts else None,
                        loss_pct=0,  # No loss if we got responses
                        asn=None,
                        org=None,
                        prefix=None,
                        country=None,
                        rir=None,
                        allocated=None,
                    )
                )
                continue

            # Try to match multi-hop line (load balancing)
            multi_match = multi_hop_pattern.match(line)
            if multi_match:
                hop_number = int(multi_match.group(1))
                hostname1 = multi_match.group(2).strip()
                ip1 = multi_match.group(3)
                rtt1 = float(multi_match.group(4))
                rtt2 = float(multi_match.group(5)) if multi_match.group(5) else None
                hostname2 = multi_match.group(6).strip()
                ip2 = multi_match.group(7)
                rtt3 = float(multi_match.group(8))

                _log.debug(
                    f"Line {i:2d}: MULTI HOP - {hop_number}: {hostname1} ({ip1}) and {hostname2} ({ip2})"
                )

                # For multi-hop, we'll create one hop with the first IP and include the second in display
                display_hostname = f"{hostname1} / {hostname2}"

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
                        last_rtt=rtt3 if rtt3 else (rtt2 if rtt2 else rtt1),
                        best_rtt=min(x for x in [rtt1, rtt2, rtt3] if x is not None),
                        worst_rtt=max(x for x in [rtt1, rtt2, rtt3] if x is not None),
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
                    f"Final hop {hop.hop_number}: {hop.ip_address} ({hop.hostname}) - RTTs: {hop.rtt1}/{hop.rtt2}/{hop.rtt3}"
                )

        _log.info(f"Parsed {len(hops)} hops from Arista traceroute")

        # Extract packet size and max hops from header if available
        max_hops = 30  # Default from your examples
        packet_size = 60  # Default from your examples

        for line in text.split("\n"):
            if "hops max" in line and "byte packets" in line:
                # Example: "traceroute to 177.72.245.178 (177.72.245.178), 30 hops max, 60 byte packets"
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


class TraceroutePluginArista(OutputPlugin):
    """Parse Arista traceroute output."""

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: t.Sequence[str] = ("arista_eos",)
    directives: t.Sequence[str] = ("__hyperglass_arista_eos_traceroute__",)
    common: bool = False

    def process(self, output: "OutputType", query: "Query") -> "OutputType":
        """Process Arista traceroute output."""
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

        return parse_arista_traceroute(
            output=output,
            target=target,
            source=source,
        )
