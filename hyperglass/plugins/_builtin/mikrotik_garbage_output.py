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
        # Remove command echoes and paging, keep only header markers and data lines
        # We'll split the output into discrete tables (each table begins at a header)
        tables: t.List[t.List[str]] = []
        current_table: t.List[str] = []
        header_line: t.Optional[str] = None

        for line in lines:
            stripped = line.strip()

            # Skip empty lines and interactive paging prompts
            if not stripped or "-- [Q quit|C-z pause]" in stripped or "-- [Q quit|D dump|C-z pause]" in stripped:
                continue

            # Skip command echo lines
            if "tool traceroute" in stripped:
                continue

            # If this is a header line, start a new table
            if "ADDRESS" in stripped and "LOSS" in stripped and "SENT" in stripped:
                header_line = line
                # If we were collecting a table, push it
                if current_table:
                    tables.append(current_table)
                    current_table = []
                # Start collecting after header
                continue

            # Collect data lines (will be associated with the most recent header)
            if header_line is not None:
                current_table.append(line)

        # Push the last collected table if any
        if current_table:
            tables.append(current_table)

        # If we didn't find any header/data, return cleaned minimal output
        if not tables:
            # Fallback to previous behavior: remove prompts and flags
            filtered_lines: t.List[str] = []
            in_flags_section = False
            for line in lines:
                stripped_line = line.strip()
                if stripped_line.startswith("@") and stripped_line.endswith("] >"):
                    continue
                if "[Q quit|D dump|C-z pause]" in stripped_line:
                    continue
                if stripped_line.startswith("Flags:"):
                    in_flags_section = True
                    continue
                if in_flags_section:
                    if "=" in stripped_line:
                        in_flags_section = False
                    else:
                        continue
                filtered_lines.append(line)
            return "\n".join(filtered_lines)

        # Aggregate tables by hop index. For each hop position, pick the row with the
        # highest SENT count. If SENT ties, prefer non-timeout rows and the later table.
        processed_lines: t.List[str] = []

        # Regex to extract LOSS% and SENT count following it: e.g. '0%    3'
        sent_re = re.compile(r"(\d+)%\s+(\d+)\b")

        max_rows = max(len(t) for t in tables)

        for i in range(max_rows):
            best_row = None
            best_sent = -1
            best_is_timeout = True
            best_table_index = -1

            for ti, table in enumerate(tables):
                if i >= len(table):
                    continue
                row = table[i]
                m = sent_re.search(row)
                if m:
                    try:
                        sent = int(m.group(2))
                    except Exception:
                        sent = 0
                else:
                    sent = 0

                is_timeout = "timeout" in row.lower() or ("100%" in row and "timeout" in row.lower())

                # Prefer higher SENT, then prefer non-timeout, then later table (higher ti)
                pick = False
                if sent > best_sent:
                    pick = True
                elif sent == best_sent:
                    if best_is_timeout and not is_timeout:
                        pick = True
                    elif (best_is_timeout == is_timeout) and ti > best_table_index:
                        pick = True

                if pick:
                    best_row = row
                    best_sent = sent
                    best_is_timeout = is_timeout
                    best_table_index = ti

            if best_row is not None:
                processed_lines.append(best_row)

        # Collapse excessive trailing timeouts into an aggregation line
        trailing_timeouts = 0
        for line in reversed(processed_lines):
            if ("timeout" in line.lower()) or (sent_re.search(line) and sent_re.search(line).group(1) == "100"):
                trailing_timeouts += 1
            else:
                break

        if trailing_timeouts > 3:
            non_trailing = len(processed_lines) - trailing_timeouts
            # Keep first 2 of trailing timeouts and aggregate the rest
            aggregated = processed_lines[:non_trailing] + processed_lines[non_trailing:non_trailing + 2]
            remaining = trailing_timeouts - 2
            aggregated.append(f"                                 ... ({remaining} more timeout hops)")
            processed_lines = aggregated

        # Prepend header line if we have one
        header_to_use = header_line or "ADDRESS                          LOSS SENT    LAST     AVG    BEST   WORST STD-DEV STATUS"
        cleaned = [header_to_use] + processed_lines
        return "\n".join(cleaned)

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

        # Minimal debug logging: log number of cleaned blocks and if any aggregation occurred
        if len(output) > 0:
            log.debug(f"MikrotikGarbageOutput processed {len(output)} output blocks.")
        # If any aggregation line was added, log that event
        for cleaned in cleaned_outputs:
            if "... (" in cleaned:
                log.debug("Aggregated excessive trailing timeout hops in traceroute output.")
                break
        return tuple(cleaned_outputs)
