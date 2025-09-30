#!/usr/bin/env python3
"""Minimal debug script for MikroTik traceroute parsing without full hyperglass deps."""

import re
import typing as t
from dataclasses import dataclass

# Simulate just the parsing logic without all the hyperglass imports


@dataclass
class MikrotikTracerouteHop:
    """Individual MikroTik traceroute hop."""

    hop_number: int
    ip_address: t.Optional[str] = None
    hostname: t.Optional[str] = None
    loss_pct: t.Optional[int] = None
    sent_count: t.Optional[int] = None
    last_rtt: t.Optional[float] = None
    avg_rtt: t.Optional[float] = None
    best_rtt: t.Optional[float] = None
    worst_rtt: t.Optional[float] = None

    @property
    def is_timeout(self) -> bool:
        """Check if this hop is a timeout."""
        return self.ip_address is None or self.loss_pct == 100


@dataclass
class MikrotikTracerouteTable:
    """MikroTik Traceroute Table."""

    target: str
    source: str
    hops: t.List[MikrotikTracerouteHop]
    max_hops: int = 30
    packet_size: int = 60

    @classmethod
    def parse_text(cls, text: str, target: str, source: str) -> "MikrotikTracerouteTable":
        """Parse MikroTik traceroute output with detailed debugging."""

        # DEBUG: Log the raw input
        print(f"=== RAW MIKROTIK TRACEROUTE INPUT ===")
        print(f"Target: {target}, Source: {source}")
        print(f"Raw text length: {len(text)} characters")
        print(f"Raw text:\n{repr(text)}")
        print(f"=== END RAW INPUT ===")

        lines = text.strip().split("\n")
        print(f"Split into {len(lines)} lines")

        # DEBUG: Log each line with line numbers
        for i, line in enumerate(lines):
            print(f"Line {i:2d}: {repr(line)}")

        # Find all table starts
        table_starts = []
        for i, line in enumerate(lines):
            if ("Columns:" in line and "ADDRESS" in line) or (
                "ADDRESS" in line
                and "LOSS" in line
                and "SENT" in line
                and not line.strip().startswith(("1", "2", "3", "4", "5", "6", "7", "8", "9"))
            ):
                table_starts.append(i)
                print(f"Found table start at line {i}: {repr(line)}")

        if not table_starts:
            print("WARNING: No traceroute table headers found in output")
            return MikrotikTracerouteTable(target=target, source=source, hops=[])

        # Take the LAST table (newest/final results)
        last_table_start = table_starts[-1]
        print(
            f"Found {len(table_starts)} tables, using the last one starting at line {last_table_start}"
        )

        # Determine format by checking the header line
        header_line = lines[last_table_start].strip()
        is_columnar_format = "Columns:" in header_line
        print(f"Header line: {repr(header_line)}")
        print(f"Is columnar format: {is_columnar_format}")

        # Parse only the last table
        hops = []
        in_data_section = False
        hop_counter = 1  # For old format without hop numbers

        # Start from the last table header
        for i in range(last_table_start, len(lines)):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                print(f"Line {i}: EMPTY - skipping")
                continue

            # Skip the column header lines
            if (
                ("Columns:" in line)
                or ("ADDRESS" in line and "LOSS" in line and "SENT" in line)
                or line.startswith("#")
            ):
                in_data_section = True
                print(f"Line {i}: HEADER - entering data section: {repr(line)}")
                continue

            # Skip paging prompts
            if "-- [Q quit|C-z pause]" in line:
                print(f"Line {i}: PAGING PROMPT - breaking: {repr(line)}")
                break  # End of this table

            if in_data_section and line:
                print(f"Line {i}: PROCESSING DATA LINE: {repr(line)}")
                try:
                    if is_columnar_format:
                        # New format: "1  10.0.0.41         0%     1  0.5ms   0.5   0.5   0.5      0"
                        parts = line.split()
                        print(f"Line {i}: Columnar format, parts: {parts}")
                        if len(parts) < 3:
                            print(f"Line {i}: Too few parts ({len(parts)}), skipping")
                            continue

                        hop_number = int(parts[0])

                        # Check if there's an IP address or if it's empty (timeout hop)
                        if len(parts) >= 8 and not parts[1].endswith("%"):
                            # Normal hop with IP address
                            ip_address = parts[1] if parts[1] else None
                            loss_pct = int(parts[2].rstrip("%"))
                            sent_count = int(parts[3])
                            last_rtt_str = parts[4]
                            avg_rtt_str = parts[5]
                            best_rtt_str = parts[6]
                            worst_rtt_str = parts[7]
                        elif len(parts) >= 4 and parts[1].endswith("%"):
                            # Timeout hop without IP address
                            ip_address = None
                            loss_pct = int(parts[1].rstrip("%"))
                            sent_count = int(parts[2])
                            last_rtt_str = parts[3] if len(parts) > 3 else "timeout"
                            avg_rtt_str = "timeout"
                            best_rtt_str = "timeout"
                            worst_rtt_str = "timeout"
                        else:
                            print(f"Line {i}: Doesn't match columnar patterns, skipping")
                            continue
                    else:
                        # Old format: "196.60.8.198                       0%    1  17.1ms    17.1    17.1    17.1       0"
                        parts = line.split()
                        print(f"Line {i}: Old format, parts: {parts}")
                        if len(parts) < 6:
                            print(f"Line {i}: Too few parts ({len(parts)}), skipping")
                            continue

                        ip_address = parts[0] if not parts[0].endswith("%") else None

                        # Handle truncated IPv6 addresses that end with "..."
                        if ip_address and ip_address.endswith("..."):
                            print(
                                f"Line {i}: Truncated IPv6 address detected: {ip_address}, setting to None"
                            )
                            ip_address = None

                        if ip_address:
                            loss_pct = int(parts[1].rstrip("%"))
                            sent_count = int(parts[2])
                            last_rtt_str = parts[3]
                            avg_rtt_str = parts[4]
                            best_rtt_str = parts[5]
                            worst_rtt_str = parts[6] if len(parts) > 6 else parts[5]
                        else:
                            # Timeout line
                            loss_pct = int(parts[0].rstrip("%"))
                            sent_count = int(parts[1])
                            last_rtt_str = "timeout"
                            avg_rtt_str = "timeout"
                            best_rtt_str = "timeout"
                            worst_rtt_str = "timeout"

                    # Convert timing values
                    def parse_rtt(rtt_str: str) -> t.Optional[float]:
                        if rtt_str in ("timeout", "-", "0ms"):
                            return None
                        # Remove 'ms' suffix and convert to float
                        rtt_clean = re.sub(r"ms$", "", rtt_str)
                        try:
                            return float(rtt_clean)
                        except ValueError:
                            return None

                    if is_columnar_format:
                        # Use hop number from the data
                        final_hop_number = hop_number
                    else:
                        # Use sequential numbering for old format
                        final_hop_number = hop_counter
                        hop_counter += 1

                    hop_obj = MikrotikTracerouteHop(
                        hop_number=final_hop_number,
                        ip_address=ip_address,
                        hostname=None,  # MikroTik doesn't do reverse DNS by default
                        loss_pct=loss_pct,
                        sent_count=sent_count,
                        last_rtt=parse_rtt(last_rtt_str),
                        avg_rtt=parse_rtt(avg_rtt_str),
                        best_rtt=parse_rtt(best_rtt_str),
                        worst_rtt=parse_rtt(worst_rtt_str),
                    )

                    hops.append(hop_obj)
                    print(
                        f"Line {i}: Created hop {final_hop_number}: {ip_address} - {loss_pct}% - {sent_count} sent"
                    )

                except (ValueError, IndexError) as e:
                    print(f"Failed to parse line '{line}': {e}")
                    continue

        print(f"Before deduplication: {len(hops)} hops")

        # For old format, we need to deduplicate by IP and take only final stats
        if not is_columnar_format and hops:
            # For old format, we need to deduplicate by IP and take only final stats
            print(f"Old format detected - deduplicating {len(hops)} total entries")

            # Group by IP address and take the HIGHEST SENT count (final stats)
            ip_to_final_hop = {}
            ip_to_max_sent = {}
            hop_order = []

            for hop in hops:
                # Use IP address if available, otherwise use hop position for truncated addresses
                if hop.ip_address:
                    ip_key = hop.ip_address
                elif hop.ip_address is None:
                    ip_key = f"truncated_hop_{hop.hop_number}"
                else:
                    ip_key = f"timeout_{hop.hop_number}"

                # Track first appearance order
                if ip_key not in hop_order:
                    hop_order.append(ip_key)
                    ip_to_max_sent[ip_key] = 0
                    print(f"New IP discovered: {ip_key}")

                # Keep hop with highest SENT count (most recent/final stats)
                if hop.sent_count and hop.sent_count >= ip_to_max_sent[ip_key]:
                    ip_to_max_sent[ip_key] = hop.sent_count
                    ip_to_final_hop[ip_key] = hop
                    print(f"Updated {ip_key}: SENT={hop.sent_count} (final stats)")

            print(f"IP order: {hop_order}")
            print(f"Final IP stats: {[(ip, ip_to_max_sent[ip]) for ip in hop_order]}")

            # Rebuild hops list with final stats and correct hop numbers
            final_hops = []
            for i, ip_key in enumerate(hop_order, 1):
                final_hop = ip_to_final_hop[ip_key]
                final_hop.hop_number = i  # Correct hop numbering
                final_hops.append(final_hop)
                print(
                    f"Final hop {i}: {ip_key} - Loss: {final_hop.loss_pct}% - Sent: {final_hop.sent_count}"
                )

            hops = final_hops
            print(f"Deduplication complete: {len(hops)} unique hops with final stats")

        print(f"After processing: {len(hops)} final hops")
        for hop in hops:
            print(
                f"Final hop {hop.hop_number}: {hop.ip_address} - {hop.loss_pct}% loss - {hop.sent_count} sent"
            )

        return MikrotikTracerouteTable(target=target, source=source, hops=hops)


if __name__ == "__main__":
    # Test with the actual IPv6 traceroute output that has truncated addresses
    mikrotik_output = """ADDRESS                          LOSS SENT    LAST     AVG    BEST   WORST STD-DEV STATUS                                                                                                                                                                                                                                                                                                                                                                                                                                     
2001:43f8:6d1::71:114              0%    1    20ms      20      20      20       0                                                                                                                                                                                                                                                                                                                                                                                                                                            
2620:0:1cff:dead:beef::5e0         0%    1   0.1ms     0.1     0.1     0.1       0                                                                                                                                                                                                                                                                                                                                                                                                                                            
2620:0:1cff:dead:beef::30e3        0%    1   0.1ms     0.1     0.1     0.1       0                                                                                                                                                                                                                                                                                                                                                                                                                                            
2a03:2880:f066:ffff::7             0%    1   0.2ms     0.2     0.2     0.2       0                                                                                                                                                                                                                                                                                                                                                                                                                                            
2a03:2880:f163:81:face:b00c:0...   0%    1   0.1ms     0.1     0.1     0.1       0                                                                                                                                                                                                                                                                                                                                                                                                                                            
2001:43f8:6d1::71:114              0%    2   0.9ms    10.5     0.9      20     9.6                                                                                                                                                                                                                                                                                                                                                                                                                                            
2620:0:1cff:dead:beef::5e0         0%    2   0.1ms     0.1     0.1     0.1       0                                                                                                                                                                                                                                                                                                                                                                                                                                            
2620:0:1cff:dead:beef::30e3        0%    2   0.2ms     0.2     0.1     0.2     0.1                                                                                                                                                                                                                                                                                                                                                                                                                                            
2a03:2880:f066:ffff::7             0%    2   0.1ms     0.2     0.1     0.2     0.1                                                                                                                                                                                                                                                                                                                                                                                                                                            
2a03:2880:f163:81:face:b00c:0...   0%    2     0ms     0.1       0     0.1     0.1                                                                                                                                                                                                                                                                                                                                                                                                                                            
2001:43f8:6d1::71:114              0%    3   0.8ms     7.2     0.8      20       9                                                                                                                                                                                                                                                                                                                                                                                                                                            
2620:0:1cff:dead:beef::5e0         0%    3   0.1ms     0.1     0.1     0.1       0                                                                                                                                                                                                                                                                                                                                                                                                                                            
2620:0:1cff:dead:beef::30e3        0%    3   0.2ms     0.2     0.1     0.2       0                                                                                                                                                                                                                                                                                                                                                                                                                                            
2a03:2880:f066:ffff::7             0%    3   0.1ms     0.1     0.1     0.2       0                                                                                                                                                                                                                                                                                                                                                                                                                                            
2a03:2880:f163:81:face:b00c:0...   0%    3   0.1ms     0.1       0     0.1       0"""

    print("Testing MikroTik IPv6 traceroute parser with truncated address...")
    result = MikrotikTracerouteTable.parse_text(
        mikrotik_output, "2a03:2880:f163:81:face:b00c:0:25de", "CAPETOWN_ZA"
    )

    print(f"\n=== FINAL RESULTS ===")
    print(f"Target: {result.target}")
    print(f"Source: {result.source}")
    print(f"Number of hops: {len(result.hops)}")
    for hop in result.hops:
        print(
            f"  Hop {hop.hop_number}: {hop.ip_address or '<truncated>'} - {hop.loss_pct}% loss - {hop.sent_count} sent - {hop.avg_rtt}ms avg"
        )
