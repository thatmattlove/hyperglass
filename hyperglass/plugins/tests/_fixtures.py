# Project
from hyperglass.models.config.devices import Device


class MockDevice(Device):
    def has_directives(self, *_: str) -> bool:
        return True
