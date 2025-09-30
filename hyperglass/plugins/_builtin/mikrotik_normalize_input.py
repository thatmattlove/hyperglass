# Standard Library
from ipaddress import ip_network, ip_address
import typing as t

# Third Party
from pydantic import PrivateAttr

# Project
from hyperglass.log import log

# REMOVIDA a importação direta de Query para evitar o erro circular
# from hyperglass.models.api.query import Query

# Local
from .._input import InputPlugin, InputPluginValidationReturn


class MikrotikTargetNormalizerInput(InputPlugin):
    """
    InputPlugin to normalize a target IP address to its network prefix.
    This ensures that queries for different IPs within the same subnet
    resolve to the same cache key.
    """

    _hyperglass_builtin: bool = PrivateAttr(False)
    name: str = "mikrotik_normalizer"
    platforms: t.Sequence[str] = ("mikrotik_routeros", "mikrotik_switchos", "mikrotik")

    # #############################################################
    # INÍCIO DA MODIFICAÇÃO: Usar 't.Any' em vez de 'Query'
    # #############################################################
    def validate(self, query: t.Any) -> InputPluginValidationReturn:
        # #############################################################
        # FIM DA MODIFICAÇÃO
        # #############################################################
        """
        Takes the query object and modifies the target if it's a BGP Route query.
        """

        # Acessamos os atributos normalmente, pois sabemos que o objeto 'query' os terá.
        if query.query_type != "bgp_route":
            return True, None

        try:
            target_ip = ip_address(query.target)

            if target_ip.version == 4:
                prefix_len = 24
            else:
                prefix_len = 48

            network = ip_network(f"{str(target_ip)}/{prefix_len}", strict=False)

            normalized_target = str(network.with_prefixlen)

            if query.target != normalized_target:
                log.debug(
                    f"Normalizing target '{query.target}' to network prefix "
                    f"'{normalized_target}' for MikroTik cache key."
                )
                query.target = normalized_target

        except ValueError:
            pass

        return True, None
