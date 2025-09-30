"""Example traceroute parsing module."""

# Standard Library
import re
import typing as t

# Project
from hyperglass.log import log
from hyperglass.models.data.traceroute import TracerouteResult, TracerouteHop

# Local
from ..main import HyperglassModel


class TracerouteParser(HyperglassModel):
    """Base traceroute parser."""

    @classmethod
    def parse_text(cls, text: str, target: str, source: str) -> TracerouteResult:
        """Parse traceroute text output into structured data."""
        _log = log.bind(parser="TracerouteParser")

        hops = []
        lines = text.strip().split("\n")

        # Common traceroute pattern: hop number, IP/hostname, RTT values
        hop_pattern = re.compile(r"^\s*(\d+)\s+(?:(\S+)\s+\(([^)]+)\)|(\S+))\s+(.+)$")

        # RTT pattern to extract timing values
        rtt_pattern = re.compile(r"(\d+(?:\.\d+)?)\s*ms")

        for line in lines:
            line = line.strip()
            if not line or line.startswith("traceroute"):
                continue

            # Handle timeout lines (* * *)
            if "*" in line and re.search(r"\d+\s+\*", line):
                hop_match = re.match(r"^\s*(\d+)\s+\*", line)
                if hop_match:
                    hop_number = int(hop_match.group(1))
                    hops.append(
                        TracerouteHop(
                            hop_number=hop_number,
                            ip_address=None,
                            hostname=None,
                            rtt1=None,
                            rtt2=None,
                            rtt3=None,
                        )
                    )
                continue

            # Parse normal hop lines
            hop_match = hop_pattern.match(line)
            if hop_match:
                hop_number = int(hop_match.group(1))

                # Extract hostname and IP
                if hop_match.group(2) and hop_match.group(3):
                    # Format: hostname (ip)
                    hostname = hop_match.group(2)
                    ip_address = hop_match.group(3)
                else:
                    # Format: ip or hostname only
                    hostname = None
                    ip_address = hop_match.group(4)

                # Extract RTT values
                rtt_text = hop_match.group(5)
                rtts = rtt_pattern.findall(rtt_text)

                # Pad with None if less than 3 RTT values
                while len(rtts) < 3:
                    rtts.append(None)

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip_address,
                        hostname=hostname,
                        rtt1=float(rtts[0]) if rtts[0] else None,
                        rtt2=float(rtts[1]) if rtts[1] else None,
                        rtt3=float(rtts[2]) if rtts[2] else None,
                    )
                )

        result = TracerouteResult(target=target, source=source, hops=hops)

        _log.info(f"Parsed {len(hops)} hops from traceroute output")
        return result


class CiscoTracerouteParser(TracerouteParser):
    """Cisco-specific traceroute parser."""

    @classmethod
    def parse_text(cls, text: str, target: str, source: str) -> TracerouteResult:
        """Parse Cisco traceroute output."""
        _log = log.bind(parser="CiscoTracerouteParser")

        # Cisco traceroute often has format like:
        # Type escape sequence to abort.
        # Tracing the route to 8.8.8.8 (8.8.8.8)
        # 1 192.168.1.1 4 msec 8 msec 4 msec

        lines = text.strip().split("\n")
        hops = []

        for line in lines:
            line = line.strip()
            if not line or "escape sequence" in line.lower() or "tracing" in line.lower():
                continue

            # Cisco format: hop_number ip_or_hostname rtt1 msec rtt2 msec rtt3 msec
            cisco_pattern = re.compile(
                r"^\s*(\d+)\s+(\S+)\s+(\d+(?:\.\d+)?)\s*msec\s+(\d+(?:\.\d+)?)\s*msec\s+(\d+(?:\.\d+)?)\s*msec"
            )

            match = cisco_pattern.match(line)
            if match:
                hop_number = int(match.group(1))
                ip_or_hostname = match.group(2)
                rtt1 = float(match.group(3))
                rtt2 = float(match.group(4))
                rtt3 = float(match.group(5))

                # Try to determine if it's an IP or hostname
                import ipaddress

                try:
                    ipaddress.ip_address(ip_or_hostname)
                    ip_address = ip_or_hostname
                    hostname = None
                except ValueError:
                    ip_address = None
                    hostname = ip_or_hostname

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip_address,
                        hostname=hostname,
                        rtt1=rtt1,
                        rtt2=rtt2,
                        rtt3=rtt3,
                    )
                )

        result = TracerouteResult(target=target, source=source, hops=hops)

        _log.info(f"Parsed {len(hops)} hops from Cisco traceroute output")
        return result


class JuniperTracerouteParser(TracerouteParser):
    """Juniper-specific traceroute parser."""

    @classmethod
    def parse_text(cls, text: str, target: str, source: str) -> TracerouteResult:
        """Parse Juniper traceroute output."""
        _log = log.bind(parser="JuniperTracerouteParser")

        # Juniper format often like:
        # traceroute to 8.8.8.8 (8.8.8.8), 30 hops max, 60 byte packets
        # 1  192.168.1.1 (192.168.1.1)  1.234 ms  1.456 ms  1.678 ms

        lines = text.strip().split("\n")
        hops = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith("traceroute to"):
                continue

            # Juniper format often has hostname (ip) followed by RTTs
            juniper_pattern = re.compile(
                r"^\s*(\d+)\s+(?:(\S+)\s+\(([^)]+)\)|(\S+))\s+([\d\.\s\*ms]+)$"
            )

            match = juniper_pattern.match(line)
            if match:
                hop_number = int(match.group(1))

                if match.group(2) and match.group(3):
                    hostname = match.group(2)
                    ip_address = match.group(3)
                else:
                    hostname = None
                    ip_address = match.group(4)

                # Extract RTT values
                rtt_text = match.group(5)
                rtts = re.findall(r"(\d+(?:\.\d+)?)\s*ms", rtt_text)

                # Handle * for timeouts
                if "*" in rtt_text:
                    timeout_count = rtt_text.count("*")
                    rtts.extend([None] * timeout_count)

                # Ensure we have exactly 3 RTT values
                while len(rtts) < 3:
                    rtts.append(None)

                hops.append(
                    TracerouteHop(
                        hop_number=hop_number,
                        ip_address=ip_address,
                        hostname=hostname,
                        rtt1=float(rtts[0]) if rtts[0] else None,
                        rtt2=float(rtts[1]) if rtts[1] else None,
                        rtt3=float(rtts[2]) if rtts[2] else None,
                    )
                )

        result = TracerouteResult(target=target, source=source, hops=hops)

        _log.info(f"Parsed {len(hops)} hops from Juniper traceroute output")
        return result


# Parser mapping by platform
TRACEROUTE_PARSERS = {
    "cisco_ios": CiscoTracerouteParser,
    "cisco_nxos": CiscoTracerouteParser,
    "cisco_xr": CiscoTracerouteParser,
    "juniper": JuniperTracerouteParser,
    "juniper_junos": JuniperTracerouteParser,
    "generic": TracerouteParser,  # Fallback
}


def get_traceroute_parser(platform: str) -> t.Type[TracerouteParser]:
    """Get the appropriate traceroute parser for a platform."""
    return TRACEROUTE_PARSERS.get(platform, TracerouteParser)
