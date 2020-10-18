"""Validate command configuration variables."""

# Local
from .tnsr import TNSRCommands
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
    "arista": AristaCommands,
    "cisco_ios": CiscoIOSCommands,
    "cisco_nxos": CiscoNXOSCommands,
    "cisco_xr": CiscoXRCommands,
    "huawei": HuaweiCommands,
    "juniper": JuniperCommands,
    "mikrotik_routeros": MikrotikRouterOS,
    "mikrotik_switchos": MikrotikSwitchOS,
    "tnsr": TNSRCommands,
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
    mikrotik_switchos: CommandGroup = MikrotikSwitchOS()
    tnsr: CommandGroup = TNSRCommands()
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
