"""Test generic utilities."""

# Standard Library
import asyncio

# Third Party
import pytest

# Local
from ..tools import (
    at_least,
    compare_init,
    get_fmt_keys,
    compare_dicts,
    compare_lists,
    dict_to_kwargs,
    snake_to_camel,
    parse_exception,
    repr_from_attrs,
    deep_convert_keys,
    split_on_uppercase,
    run_coroutine_in_new_thread,
)


def test_split_on_uppercase():
    strings = (
        ("TestOne", ["Test", "One"]),
        ("testTwo", ["test", "Two"]),
        ("TestingOneTwoThree", ["Testing", "One", "Two", "Three"]),
    )
    for str_in, list_out in strings:
        result = split_on_uppercase(str_in)
        assert result == list_out


def test_parse_exception():
    with pytest.raises(TypeError):
        parse_exception(1)

    exc1 = RuntimeError("Test1")
    exc1_expected = f"Runtime Error ({(RuntimeError.__doc__ or '').strip('.')})"
    exc2 = RuntimeError("Test2")
    exc2_cause = f"Connection Error ({(ConnectionError.__doc__ or '').strip('.')})"
    exc2_expected = f"{exc1_expected}, caused by {exc2_cause}"
    try:
        raise exc1
    except Exception as err:
        result = parse_exception(err)
        assert result == exc1_expected
    try:
        raise exc2 from ConnectionError
    except Exception as err:
        result = parse_exception(err)
        assert result == exc2_expected


def test_repr_from_attrs():
    # Third Party
    from pydantic import create_model

    model = create_model("TestModel", one=(str, ...), two=(int, ...), three=(bool, ...))
    implementation = model(one="one", two=2, three=True)
    result = repr_from_attrs(implementation, ("one", "two", "three"))
    assert result == "TestModel(one='one', three=True, two=2)"


@pytest.mark.dependency()
def test_snake_to_camel():
    keys = (
        ("test_one", "testOne"),
        ("test_two_three", "testTwoThree"),
        ("Test_four_five_six", "testFourFiveSix"),
    )
    for key_in, key_out in keys:
        result = snake_to_camel(key_in)
        assert result == key_out


def test_get_fmt_keys():
    template = "This is a {template} for a {test}"
    result = get_fmt_keys(template)
    assert len(result) == 2 and "template" in result and "test" in result


@pytest.mark.dependency(
    depends=["hyperglass/util/tests/test_tools.py::test_snake_to_camel"], scope="session"
)
def test_deep_convert_keys():
    dict_in = {
        "key_one": 1,
        "key_two": 2,
        "key_dict": {
            "key_one": "one",
            "key_two": "two",
        },
        "key_list_dicts": [{"key_one": 101, "key_two": 102}, {"key_three": 103, "key_four": 104}],
    }

    result = deep_convert_keys(dict_in, snake_to_camel)
    assert result.get("keyOne") is not None
    assert result.get("keyTwo") is not None
    assert result.get("keyDict") is not None
    assert result["keyDict"].get("keyOne") is not None
    assert result["keyDict"].get("keyTwo") is not None
    assert isinstance(result.get("keyListDicts"), list)
    assert result["keyListDicts"][0].get("keyOne") is not None
    assert result["keyListDicts"][0].get("keyTwo") is not None
    assert result["keyListDicts"][1].get("keyThree") is not None
    assert result["keyListDicts"][1].get("keyFour") is not None


def test_at_least():
    assert at_least(8, 10) == 10
    assert at_least(8, 6) == 8


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


def test_run_coroutine_in_new_thread():
    async def sleeper():
        await asyncio.sleep(5)

    async def test():
        return True

    asyncio.run(sleeper())
    result = run_coroutine_in_new_thread(test)
    assert result is True


def test_compare_lists():
    # Standard Library
    import random

    list1 = ["one", 2, "3"]
    list2 = [4, "5", "six"]
    list3 = ["one", 11, False]
    list4 = [*list1, *list2]
    random.shuffle(list4)
    assert compare_lists(list1, list2) is False
    assert compare_lists(list1, list3) is False
    assert compare_lists(list1, list4) is True


def test_dict_to_kwargs():
    class Test:
        one: int
        two: int

        def __init__(self, **kw) -> None:
            for k, v in kw.items():
                setattr(self, k, v)

        def __repr__(self) -> str:
            return "Test(one={}, two={})".format(self.one, self.two)

    d1 = {"one": 1, "two": 2}
    e1 = "one=1 two=2"
    d2 = {"cls": Test(one=1, two=2), "three": "three"}
    e2 = "cls=Test(one=1, two=2) three='three'"
    r1 = dict_to_kwargs(d1)
    assert r1 == e1
    r2 = dict_to_kwargs(d2)
    assert r2 == e2
