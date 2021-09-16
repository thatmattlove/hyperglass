"""Test RPKI data fetching."""
# Third Party
import pytest

# Local
from ..rpki import RPKI_NAME_MAP, rpki_state

TEST_STATES = (
    ("103.21.244.0/24", 13335, 0),
    ("1.1.1.0/24", 13335, 1),
    ("192.0.2.0/24", 65000, 2),
)


@pytest.mark.dependency()
def test_rpki():
    for prefix, asn, expected in TEST_STATES:
        result = rpki_state(prefix, asn)
        result_name = RPKI_NAME_MAP.get(result, "No Name")
        expected_name = RPKI_NAME_MAP.get(expected, "No Name")
        assert (
            result == expected
        ), "RPKI State for '{}' via AS{!s} '{}' ({}) instead of '{}' ({})".format(
            prefix, asn, result, result_name, expected, expected_name
        )
