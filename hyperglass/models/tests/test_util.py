"""Test model utilities."""

# Third Party
import pytest

# Local
from ..util import check_legacy_fields


def test_check_legacy_fields():
    test1 = {"name": "Device A", "nos": "juniper"}
    test1_expected = {"name": "Device A", "type": "juniper"}
    test2 = {"name": "Device B", "type": "juniper"}
    test3 = {"name": "Device C"}
    assert set(check_legacy_fields("Device", **test1).keys()) == set(
        test1_expected.keys()
    ), "legacy field not replaced"
    assert set(check_legacy_fields("Device", **test2).keys()) == set(
        test2.keys()
    ), "new field not left unmodified"
    with pytest.raises(ValueError):
        check_legacy_fields("Device", **test3)
