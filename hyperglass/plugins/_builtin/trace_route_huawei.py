"""Parse Huawei traceroute output to structured data."""

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


def parse_huawei_traceroute(
    output: t.Union[str, t.Sequence[str]], target: str, source: str
) -> "OutputDataModel":
    """Parse a Huawei traceroute text response."""
    result = None
    out_list = _normalize_output(output)

    _log = log.bind(plugin=TraceroutePluginHuawei.__name__)
    combined_output = "\n".join(out_list)

    # DEBUG: Log the raw output we're about to parse
    _log.debug(f"=== HUAWEI TRACEROUTE PLUGIN RAW INPUT ===")
    _log.debug(f"Target: {target}, Source: {source}")
    _log.debug(f"Output pieces: {len(out_list)}")
    _log.debug(f"Combined output length: {len(combined_output)}")
    _log.debug(f"First 500 chars: {repr(combined_output[:500])}")
    _log.debug(f"=== END PLUGIN RAW INPUT ===")

    try:
        result = HuaweiTracerouteTable.parse_text(combined_output, target, source)
    except Exception as exc:
        _log.error(f"Failed to parse Huawei traceroute: {exc}")
        raise ParsingError(f"Failed to parse Huawei traceroute output: {exc}") from exc

    _log.debug(f"=== FINAL STRUCTURED TRACEROUTE RESULT ===")
    _log.debug(f"Successfully parsed {len(result.hops)} traceroute hops")
    _log.debug(f"Target: {target}, Source: {source}")
    for hop in result.hops:
        _log.debug(f"Hop {hop.hop_number}: {hop.ip_address or '*'} - RTT: {hop.rtt1 or 'timeout'}")
    _log.debug(f"Raw output length: {len(combined_output)} characters")
    _log.debug(f"=== END STRUCTURED RESULT ===")

    return result


class HuaweiTracerouteTable(TracerouteResult):
    """Huawei traceroute table parser."""

    @classmethod
    def parse_text(cls, text: str, target: str, source: str) -> TracerouteResult:
        """Parse Huawei traceroute text output into structured data."""
        _log = log.bind(parser="HuaweiTracerouteTable")

        _log.debug(f"=== RAW HUAWEI TRACEROUTE INPUT ===")
        _log.debug(f"Target: {target}, Source: {source}")
        _log.debug(f"Raw text length: {len(text)} characters")
        _log.debug(f"Raw text:\n{repr(text)}")
        _log.debug(f"=== END RAW INPUT ===")

        hops = []
        lines = text.strip().split("\n")

        _log.debug(f"Split into {len(lines)} lines")

        # Pattern for normal hop: "1 172.24.165.197 1 ms"
        hop_pattern = re.compile(r"^\s*(\d+)\s+(\S+)\s+(\d+(?:\.\d+)?)\s*ms\s*$")

        # Pattern for timeout hop: "3  *"
        timeout_pattern = re.compile(r"^\s*(\d+)\s+\*\s*$")

        for i, line in enumerate(lines):
            line = line.strip()
            _log.debug(f"Line {i:2d}: {repr(line)}")

            if not line:
                continue

            # Skip header lines
            if (
                "traceroute to" in line.lower()
                or "max hops" in line.lower()
                or "press CTRL_C" in line.lower()
            ):
                _log.debug(f"Line {i:2d}: SKIPPING HEADER")
                continue

            # Try to match normal hop
            hop_match = hop_pattern.match(line)
            if hop_match:
                hop_number = int(hop_match.group(1))
                ip_address = hop_match.group(2)
                rtt = float(hop_match.group(3))

                _log.debug(f"Line {i:2d}: NORMAL HOP - {hop_number}: {ip_address} {rtt}ms")

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip_address,
                        display_ip=None,  # Huawei doesn't truncate IPs like MikroTik
                        hostname=None,  # Will be populated by IP enrichment
                        rtt1=rtt,
                        rtt2=None,  # Huawei shows only one RTT per line
                        rtt3=None,
                        # MikroTik-specific statistics (populate for consistency)
                        sent_count=1,  # Huawei sends 1 ping per hop
                        last_rtt=rtt,  # Same as the only RTT
                        best_rtt=rtt,  # Same as the only RTT
                        worst_rtt=rtt,  # Same as the only RTT
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

            # Try to match timeout hop
            timeout_match = timeout_pattern.match(line)
            if timeout_match:
                hop_number = int(timeout_match.group(1))

                _log.debug(f"Line {i:2d}: TIMEOUT HOP - {hop_number}: *")

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=None,
                        display_ip=None,
                        hostname=None,
                        rtt1=None,
                        rtt2=None,
                        rtt3=None,
                        # MikroTik-specific statistics for timeout
                        sent_count=1,  # Still sent 1 ping, just timed out
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
                _log.debug(f"Final hop {hop.hop_number}: {hop.ip_address} - {hop.rtt1}ms")

        _log.info(f"Parsed {len(hops)} hops from Huawei traceroute")

        return TracerouteResult(
            target=target,
            source=source,
            hops=hops,
            max_hops=64,  # Default for Huawei
            packet_size=40,  # From the header in sample output
            raw_output=text,
            asn_organizations={},
        )


class TraceroutePluginHuawei(OutputPlugin):
    """Parse Huawei traceroute output."""

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: t.Sequence[str] = ("huawei", "huawei_vrpv8")
    directives: t.Sequence[str] = ("__hyperglass_huawei_traceroute__",)
    common: bool = False

    def process(self, output: "OutputType", query: "Query") -> "OutputType":
        """Process Huawei traceroute output."""
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

        return parse_huawei_traceroute(
            output=output,
            target=target,
            source=source,
        )
