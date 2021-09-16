"""Test typing utilities."""
# flake8: noqa

# Standard Library
import typing

# Local
from ..typing import is_type, is_series


class EmptyTestClass:
    pass


class EmptySubClass(EmptyTestClass):
    pass


_string = "Test String"
_string_empty = ""
_dict = {"one": 1, "two": 2}
_dict_empty = dict()
_list = [1, 2, 3]
_list_empty = []
_set = {"one", "two"}
_set_empty = set()
_tuple = (1, 2, 3)
_tuple_empty = tuple()
_class = EmptyTestClass
_class_instance = EmptyTestClass()
_subclass = EmptySubClass
_subclass_instance = EmptySubClass()

DictOrString = typing.Union[typing.Dict, str]
ClassOrString = typing.Union[EmptyTestClass, str]


def test_is_type():
    checks = (
        ("Non-Empty String is String", True, _string, str),
        ("Empty String is String", True, _string_empty, str),
        ("Non-Empty Dict is Dict", True, _dict, typing.Dict),
        ("Empty Dict is Dict", True, _dict_empty, dict),
        ("Non-Empty List is List", True, _list, typing.List),
        ("Empty List is List", True, _list_empty, list),
        ("Non-Empty Tuple is Tuple", True, _tuple, typing.Tuple),
        ("Empty Tuple is Tuple", True, _tuple_empty, tuple),
        ("Non-Empty Set is Set", True, _set, typing.Set),
        ("Empty Set is Set", True, _set_empty, set),
        ("Non-Empty String is Dict or String", True, _string, DictOrString),
        ("Non-Empty Dict is Dict or String", True, _dict, DictOrString),
        ("Non-Empty List is Dict or String", False, _list, DictOrString),
        ("Empty list is Dict or String", False, _list_empty, DictOrString),
        ("Class object is Class object", False, _class, _class),
        ("Class instance is Class instance", True, _class_instance, _class_instance),
        ("Class instance is Class object", True, _class_instance, _class),
        ("Subclass instance is Class instance", True, _subclass_instance, _class_instance),
        ("Subclass instance is Class object", True, _subclass_instance, _class),
        ("Class object is Class or String", False, _subclass, ClassOrString),
        ("Class instance is Class or String", True, _class_instance, ClassOrString),
        ("Subclass instance is Class or String", True, _subclass_instance, ClassOrString),
    )
    for _, expected, value, _type in checks:
        result = is_type(value, _type)
        if result is not expected:
            raise AssertionError(f"Got `{value}`, expected `{str(_type)}`")


def test_is_series():
    checks = (
        ((1, 2, 3), True),
        ([1, 2, 3], True),
        ("1,2,3", False),
        ({1, 2, 3}, True),
    )
    for value, expected in checks:
        assert is_series(value) is expected
