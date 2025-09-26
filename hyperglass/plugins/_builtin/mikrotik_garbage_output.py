"""Remove anything before the command if found in output."""

# Standard Library
import re
import typing as t

# Third Party
from pydantic import PrivateAttr

# Project
from hyperglass.log import log
from hyperglass.types import Series

# Local
from .._output import OutputType, OutputPlugin

if t.TYPE_CHECKING:
    # Project
    from hyperglass.models.api.query import Query


class MikrotikGarbageOutput(OutputPlugin):
    """Parse Mikrotik output to remove garbage before structured parsing."""

    _hyperglass_builtin: bool = PrivateAttr(True)
    platforms: t.Sequence[str] = ("mikrotik_routeros", "mikrotik_switchos", "mikrotik")
    # Apply to ALL commands on MikroTik platforms
    common: bool = True

    def _clean_traceroute_output(self, raw_output: str) -> str:
        """Clean MikroTik traceroute output specifically."""
        if not raw_output or not raw_output.strip():
            return ""

        lines = raw_output.splitlines()
        cleaned_lines = []
        found_header = False
        hop_data = {}  # IP -> (line, sent_count)

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                continue

            # Skip interactive paging prompts
            if "-- [Q quit|C-z pause]" in stripped or "-- [Q quit|D dump|C-z pause]" in stripped:
                continue

            # Skip command echo lines
            if "tool traceroute" in stripped:
                continue

            # Look for the header line (ADDRESS LOSS SENT LAST AVG BEST WORST)
            if "ADDRESS" in stripped and "LOSS" in stripped and "SENT" in stripped:
                if not found_header:
                    cleaned_lines.append(line)
                    found_header = True
                continue

            # Only process data lines after we've found the header
            if found_header and stripped:
                # Try to extract IP address (IPv4 or IPv6) from the line
                ipv4_match = re.match(r"^(\d+\.\d+\.\d+\.\d+)", stripped)
                ipv6_match = re.match(r"^([0-9a-fA-F:]+)", stripped) if not ipv4_match else None

                if ipv4_match or ipv6_match:
                    ip = ipv4_match.group(1) if ipv4_match else ipv6_match.group(1)

                    # Extract the SENT count from the line (look for pattern like "0% 3" or "100% 2")
                    sent_match = re.search(r"\s+(\d+)%\s+(\d+)\s+", stripped)
                    sent_count = int(sent_match.group(2)) if sent_match else 0

                    # Keep the line with the highest SENT count (most complete data)
                    if ip not in hop_data or sent_count > hop_data[ip][1]:
                        hop_data[ip] = (line, sent_count)
                    elif (
                        sent_count == hop_data[ip][1]
                        and "timeout" not in stripped
                        and "timeout" in hop_data[ip][0]
                    ):
                        # If SENT counts are equal, prefer non-timeout over timeout
                        hop_data[ip] = (line, sent_count)
                elif "100%" in stripped and "timeout" in stripped:
                    # Skip standalone timeout lines without IP
                    continue

        # Reconstruct the output with only the best results
        if found_header and hop_data:
            result_lines = [cleaned_lines[0]]  # Header

            # Sort by the order IPs first appeared, but use the best data for each
            seen_ips = []
            for line in lines:
                stripped = line.strip()
                if found_header:
                    ipv4_match = re.match(r"^(\d+\.\d+\.\d+\.\d+)", stripped)
                    ipv6_match = re.match(r"^([0-9a-fA-F:]+)", stripped) if not ipv4_match else None

                    if ipv4_match or ipv6_match:
                        ip = ipv4_match.group(1) if ipv4_match else ipv6_match.group(1)
                        if ip not in seen_ips and ip in hop_data:
                            seen_ips.append(ip)
                            result_lines.append(hop_data[ip][0])

            return "\n".join(result_lines)

        return raw_output

    def process(self, *, output: OutputType, query: "Query") -> Series[str]:
        """
        Clean raw output from a MikroTik device.
        This plugin removes command echoes, prompts, flag legends, and interactive help text.
        """

        # If output is already processed/structured (not raw strings), pass it through unchanged
        if not isinstance(output, (tuple, list)):
            return output

        # Check if the tuple/list contains non-string objects (structured data)
        if output and not isinstance(output[0], str):
            return output

        cleaned_outputs = []

        for raw_output in output:
            # Handle non-string outputs (already processed by other plugins) - double check
            if not isinstance(raw_output, str):
                cleaned_outputs.append(raw_output)
                continue

            # Se a saída já estiver vazia, não há nada a fazer.
            if not raw_output or not raw_output.strip():
                cleaned_outputs.append("")
                continue

            # Check if this is traceroute output and handle it specially
            if (
                "tool traceroute" in raw_output
                or ("ADDRESS" in raw_output and "LOSS" in raw_output and "SENT" in raw_output)
                or "-- [Q quit|C-z pause]" in raw_output
            ):
                cleaned_output = self._clean_traceroute_output(raw_output)
                cleaned_outputs.append(cleaned_output)
                continue

            # Original logic for other outputs (BGP routes, etc.)
            lines = raw_output.splitlines()
            filtered_lines = []
            in_flags_section = False

            for line in lines:
                stripped_line = line.strip()

                # Ignorar prompts e ecos de comando
                if stripped_line.startswith("@") and stripped_line.endswith("] >"):
                    continue

                # Ignorar a linha de ajuda interativa
                if "[Q quit|D dump|C-z pause]" in stripped_line:
                    continue

                # Iniciar a detecção da seção de Flags
                if stripped_line.startswith("Flags:"):
                    in_flags_section = True
                    continue  # Pula a própria linha "Flags:"

                # Se estivermos na seção de flags, verificar se a linha ainda é parte dela.
                if in_flags_section:
                    if "=" in stripped_line:
                        in_flags_section = False
                    else:
                        continue  # Pula as linhas da legenda de flags

                filtered_lines.append(line)

            # Juntar as linhas limpas de volta em uma única string.
            cleaned_output = "\n".join(filtered_lines)
            cleaned_outputs.append(cleaned_output)

        log.debug(f"MikrotikGarbageOutput cleaned {len(output)} output blocks.")
        return tuple(cleaned_outputs)
