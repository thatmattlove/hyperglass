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
    # Aplicar a todos os comandos para garantir a limpeza
    directives: t.Sequence[str] = (
        "__hyperglass_mikrotik_bgp_aspath__",
        "__hyperglass_mikrotik_bgp_community__",
        "__hyperglass_mikrotik_bgp_route__",
        "__hyperglass_mikrotik_ping__",
        "__hyperglass_mikrotik_traceroute__",
    )

    def process(self, *, output: OutputType, query: "Query") -> Series[str]:
        """
        Clean raw output from a MikroTik device.
        This plugin removes command echoes, prompts, flag legends, and interactive help text.
        """

        # O 'output' é uma tupla de strings, onde cada string é a saída de um comando.
        # Vamos processar cada uma delas.
        cleaned_outputs = []

        for raw_output in output:

            # Se a saída já estiver vazia, não há nada a fazer.
            if not raw_output or not raw_output.strip():
                cleaned_outputs.append("")
                continue

            # 1. Dividir a saída em linhas para processamento individual.
            lines = raw_output.splitlines()

            # 2. Filtrar as linhas de "lixo" conhecidas.
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
                # Uma linha de dados de rota real geralmente começa com flags (ex: "Ab") ou é indentada.
                # Uma linha da legenda de flags não.
                if in_flags_section:
                    # Se a linha não começar com espaço ou não tiver um "=" (sinal de dado),
                    # é provável que seja parte da legenda.
                    # A forma mais segura é procurar pelo fim da legenda.
                    # A primeira linha de dados real começa com flags ou indentação.
                    # Vamos assumir que a legenda termina quando encontramos uma linha que contém "=".
                    if "=" in stripped_line:
                        in_flags_section = False
                    else:
                        continue  # Pula as linhas da legenda de flags

                filtered_lines.append(line)

            # 3. Juntar as linhas limpas de volta em uma única string.
            cleaned_output = "\n".join(filtered_lines)
            cleaned_outputs.append(cleaned_output)

        log.debug(f"MikrotikGarbageOutput cleaned {len(output)} output blocks.")
        return tuple(cleaned_outputs)
