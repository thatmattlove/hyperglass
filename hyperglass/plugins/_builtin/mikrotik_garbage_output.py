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
    # Only apply to MikroTik platforms, not all devices
    common: bool = False

    def _clean_traceroute_output(self, raw_output: str) -> str:
        """Clean MikroTik traceroute output specifically.

        Important: Traceroute hops are sequential - each line represents a unique hop position.
        We should NOT deduplicate by IP address as the same IP can appear at different hops.
        Order matters for traceroute results.

        However, we can aggregate consecutive timeout lines at the END of the traceroute
        to avoid showing 10+ meaningless timeout entries.
        """
        if not raw_output or not raw_output.strip():
            return ""

        lines = raw_output.splitlines()
        cleaned_lines = []
        found_header = False
        data_lines = []

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

            # After finding header, collect all data lines
            if found_header and stripped:
                data_lines.append(line)

        # Process data lines to aggregate trailing timeouts
        if data_lines:
            processed_lines = []
            trailing_timeout_count = 0

            # Work backwards to count trailing timeouts
            for i in range(len(data_lines) - 1, -1, -1):
                line = data_lines[i]
                if (
                    "100%" in line.strip()
                    and "timeout" in line.strip()
                    and not line.strip().startswith(
                        ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")
                    )
                ):
                    # This is a timeout line (no IP address at start)
                    trailing_timeout_count += 1
                else:
                    # Found a non-timeout line, stop counting
                    break

            # Add non-trailing lines as-is
            non_trailing_count = len(data_lines) - trailing_timeout_count
            processed_lines.extend(data_lines[:non_trailing_count])

            # Handle trailing timeouts
            if trailing_timeout_count > 0:
                if trailing_timeout_count <= 3:
                    # If 3 or fewer trailing timeouts, show them all
                    processed_lines.extend(data_lines[non_trailing_count:])
                else:
                    # If more than 3 trailing timeouts, show first 2 and aggregate the rest
                    processed_lines.extend(data_lines[non_trailing_count : non_trailing_count + 2])
                    remaining_timeouts = trailing_timeout_count - 2
                    # Add an aggregation line
                    processed_lines.append(
                        f"                                 ... ({remaining_timeouts} more timeout hops)"
                    )

            cleaned_lines.extend(processed_lines)

        return "\n".join(cleaned_lines)

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
