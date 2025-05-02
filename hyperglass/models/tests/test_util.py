"""Test model utilities."""

# Third Party
import pytest

# Local
from ..util import check_legacy_fields


@pytest.mark.dependency()
def test_check_legacy_fields():
    test1 = {"name": "Device A", "nos": "juniper"}
    test1_expected = {"name": "Device A", "platform": "juniper"}
    test2 = {"name": "Device B", "platform": "juniper"}
    test3 = {"name": "Device C"}
    test4 = {"name": "Device D", "network": "this is wrong"}

    assert set(check_legacy_fields(model="Device", data=test1).keys()) == set(
        test1_expected.keys()
    ), "legacy field not replaced"

    assert set(check_legacy_fields(model="Device", data=test2).keys()) == set(
        test2.keys()
    ), "new field not left unmodified"

    with pytest.raises(ValueError):
        check_legacy_fields(model="Device", data=test3)

    with pytest.raises(ValueError):
        check_legacy_fields(model="Device", data=test4)
