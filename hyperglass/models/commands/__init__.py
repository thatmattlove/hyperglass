"""Validate command configuration variables."""

# Local
from .frr import FRRCommands
from .bird import BIRDCommands
from .tnsr import TNSRCommands
from .vyos import VyosCommands
from ..main import HyperglassModelExtra
from .common import CommandGroup
from .huawei import HuaweiCommands
from .juniper import JuniperCommands
from .cisco_xr import CiscoXRCommands
from .cisco_ios import CiscoIOSCommands
from .arista_eos import AristaEOSCommands
from .cisco_nxos import CiscoNXOSCommands
from .nokia_sros import NokiaSROSCommands
from .mikrotik_routeros import MikrotikRouterOS
from .mikrotik_switchos import MikrotikSwitchOS

_NOS_MAP = {
    "arista_eos": AristaEOSCommands,
    "bird_ssh": BIRDCommands,
    "cisco_ios": CiscoIOSCommands,
    "cisco_nxos": CiscoNXOSCommands,
    "cisco_xr": CiscoXRCommands,
    "frr_ssh": FRRCommands,
    "huawei": HuaweiCommands,
    "juniper": JuniperCommands,
    "mikrotik_routeros": MikrotikRouterOS,
    "mikrotik_switchos": MikrotikSwitchOS,
    "nokia_sros": NokiaSROSCommands,
    "tnsr": TNSRCommands,
    "vyos": VyosCommands,
}


class Commands(HyperglassModelExtra):
    """Base class for command definitions."""

    arista_eos: CommandGroup = AristaEOSCommands()
    bird_ssh: CommandGroup = BIRDCommands()
    cisco_ios: CommandGroup = CiscoIOSCommands()
    cisco_nxos: CommandGroup = CiscoNXOSCommands()
    cisco_xr: CommandGroup = CiscoXRCommands()
    frr_ssh: CommandGroup = FRRCommands()
    huawei: CommandGroup = HuaweiCommands()
    juniper: CommandGroup = JuniperCommands()
    mikrotik_routeros: CommandGroup = MikrotikRouterOS()
    mikrotik_switchos: CommandGroup = MikrotikSwitchOS()
    nokia_sros: CommandGroup = NokiaSROSCommands()
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
