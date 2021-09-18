"""Test generic utilities."""

# Local
from .. import compare_init, compare_dicts


def test_compare_dicts():

    d1 = {"one": 1, "two": 2}
    d2 = {"one": 1, "two": 2}
    d3 = {"one": 1, "three": 3}
    d4 = {"one": 1, "two": 3}
    d5 = {}
    d6 = {}
    checks = (
        (d1, d2, True),
        (d1, d3, False),
        (d1, d4, False),
        (d1, d1, True),
        (d5, d6, True),
        (d1, [], False),
    )
    for a, b, expected in checks:
        assert compare_dicts(a, b) is expected


def test_compare_init():
    class Compare1:
        def __init__(self, item: str) -> None:
            pass

    class Compare2:
        def __init__(self: "Compare2", item: str) -> None:
            pass

    class Compare3:
        def __init__(self: "Compare3", item: str, other_item: int) -> None:
            pass

    class Compare4:
        def __init__(self: "Compare4", item: bool) -> None:
            pass

    class Compare5:
        pass

    checks = (
        (Compare1, Compare2, True),
        (Compare1, Compare3, False),
        (Compare1, Compare4, False),
        (Compare1, Compare5, False),
        (Compare1, Compare1, True),
    )
    for a, b, expected in checks:
        assert compare_init(a, b) is expected
