"""Validate command configuration variables."""

from .vyos import VyosCommands
from ..main import HyperglassModelExtra
from .arista import AristaCommands
from .common import CommandGroup
from .huawei import HuaweiCommands
from .juniper import JuniperCommands
from .cisco_xr import CiscoXRCommands
from .cisco_ios import CiscoIOSCommands
from .cisco_nxos import CiscoNXOSCommands
from .mikrotik_routeros import MikrotikRouterOS
from .mikrotik_switchos import MikrotikSwitchOS

_NOS_MAP = {
    "juniper": JuniperCommands,
    "cisco_ios": CiscoIOSCommands,
    "cisco_xr": CiscoXRCommands,
    "cisco_nxos": CiscoNXOSCommands,
    "arista": AristaCommands,
    "huawei": HuaweiCommands,
    "mikrotik_routeros": MikrotikRouterOS,
    "mikrotik_switchos": MikrotikSwitchOS,
    "vyos": VyosCommands,
}


class Commands(HyperglassModelExtra):
    """Base class for command definitions."""

    juniper: CommandGroup = JuniperCommands()
    arista: CommandGroup = AristaCommands()
    cisco_ios: CommandGroup = CiscoIOSCommands()
    cisco_xr: CommandGroup = CiscoXRCommands()
    cisco_nxos: CommandGroup = CiscoNXOSCommands()
    huawei: CommandGroup = HuaweiCommands()
    mikrotik_routeros: CommandGroup = MikrotikRouterOS()
    mikortik_switchos: CommandGroup = MikrotikSwitchOS()
    vyos: CommandGroup = VyosCommands()

    @classmethod
    def import_params(cls, **input_params):
        """Import loaded YAML, initialize per-command definitions.

        Dynamically set attributes for the command class.

        Arguments:
            input_params {dict} -- Unvalidated command definitions

        Returns:
            {object} -- Validated commands object
        """
        obj = Commands()
        for nos, cmds in input_params.items():
            nos_cmd_set = _NOS_MAP.get(nos, CommandGroup)
            nos_cmds = nos_cmd_set(**cmds)
            setattr(obj, nos, nos_cmds)
        return obj

    class Config:
        """Override pydantic config."""

        validate_all = False
