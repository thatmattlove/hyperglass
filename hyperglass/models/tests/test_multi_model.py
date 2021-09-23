"""Test HyperglassMultiModel."""

# Third Party
from pydantic import BaseModel

# Local
from ..main import MultiModel


class Item(BaseModel):
    """Test item."""

    id: str
    name: str


class Items(MultiModel, model=Item, unique_by="id"):
    """Multi Model Test."""


ITEMS_1 = [
    {"id": "item1", "name": "Item One"},
    Item(id="item2", name="Item Two"),
    {"id": "item3", "name": "Item Three"},
]

ITEMS_2 = [
    Item(id="item4", name="Item Four"),
    {"id": "item5", "name": "Item Five"},
]

ITEMS_3 = [
    {"id": "item1", "name": "Item New One"},
    {"id": "item6", "name": "Item Six"},
]


def test_multi_model():
    model = Items(*ITEMS_1)
    assert model.count == 3
    assert len([o for o in model]) == model.count  # noqa: C416 (Iteration testing)
    assert model["item1"].name == "Item One"
    model.add(*ITEMS_2)
    assert model.count == 5
    assert model[3].name == "Item Four"
    model.add(*ITEMS_3, unique_by="id")
    assert model.count == 6
    assert model["item1"].name == "Item New One"
