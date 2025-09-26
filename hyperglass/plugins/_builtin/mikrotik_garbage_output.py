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
        unique_hops = {}
        hop_order = []
        
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
            
            # Only include data lines after we've found the header
            if found_header and stripped:
                # Try to extract IP address from the line to deduplicate
                ip_match = re.match(r'^(\d+\.\d+\.\d+\.\d+)', stripped)
                if ip_match:
                    ip = ip_match.group(1)
                    if ip not in unique_hops:
                        unique_hops[ip] = line
                        hop_order.append(ip)
                    else:
                        # Keep the line with better data (non-timeout over timeout)
                        if "timeout" not in stripped and "timeout" in unique_hops[ip]:
                            unique_hops[ip] = line
                elif "100%" in stripped and "timeout" in stripped:
                    # This is likely a timeout line without IP - skip standalone timeout lines
                    continue
                else:
                    # Keep any other data lines that might be relevant
                    cleaned_lines.append(line)
        
        # Reconstruct the output
        if found_header and (unique_hops or any("timeout" not in line for line in cleaned_lines[1:] if line.strip())):
            result_lines = [cleaned_lines[0]]  # Header
            result_lines.extend(unique_hops[ip] for ip in hop_order)
            # Add any non-IP lines that weren't already included
            for line in cleaned_lines[1:]:
                if line not in result_lines and not any(ip in line for ip in hop_order):
                    result_lines.append(line)
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
            if ("tool traceroute" in raw_output or 
                ("ADDRESS" in raw_output and "LOSS" in raw_output and "SENT" in raw_output) or
                "-- [Q quit|C-z pause]" in raw_output):
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
