"""Functions & handlers for external data."""

# Local
from .rpki import rpki_state
from .slack import SlackHook
from .generic import BaseExternal
from .msteams import MSTeams
from .bgptools import network_info, network_info_sync
from .webhooks import Webhook

__all__ = (
    "BaseExternal",
    "MSTeams",
    "network_info_sync",
    "network_info",
    "rpki_state",
    "SlackHook",
    "Webhook",
)
