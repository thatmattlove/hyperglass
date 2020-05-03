"""Validate command configuration variables."""

# Project
from hyperglass.models import HyperglassModelExtra
from hyperglass.configuration.models.commands.arista import AristaCommands
from hyperglass.configuration.models.commands.common import CommandGroup
from hyperglass.configuration.models.commands.huawei import HuaweiCommands
from hyperglass.configuration.models.commands.juniper import JuniperCommands
from hyperglass.configuration.models.commands.cisco_xr import CiscoXRCommands
from hyperglass.configuration.models.commands.cisco_ios import CiscoIOSCommands
from hyperglass.configuration.models.commands.cisco_nxos import CiscoNXOSCommands

_NOS_MAP = {
    "juniper": JuniperCommands,
    "cisco_ios": CiscoIOSCommands,
    "cisco_xr": CiscoXRCommands,
    "cisco_nxos": CiscoNXOSCommands,
    "arista": AristaCommands,
    "huawei": HuaweiCommands,
}


class Commands(HyperglassModelExtra):
    """Base class for command definitions."""

    juniper: CommandGroup = JuniperCommands()
    arista: CommandGroup = AristaCommands()
    cisco_ios: CommandGroup = CiscoIOSCommands()
    cisco_xr: CommandGroup = CiscoXRCommands()
    cisco_nxos: CommandGroup = CiscoNXOSCommands()
    huawei: CommandGroup = HuaweiCommands()

    @classmethod
    def import_params(cls, input_params):
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
