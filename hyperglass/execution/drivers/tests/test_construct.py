# Project
from hyperglass.models.api import Query
from hyperglass.configuration import init_user_config
from hyperglass.models.directive import Directives
from hyperglass.models.config.devices import Devices

# Local
from .._construct import Construct


def test_construct():

    devices = Devices(
        {
            "name": "test1",
            "address": "127.0.0.1",
            "credential": {"username": "", "password": ""},
            "platform": "juniper",
            "attrs": {"source4": "192.0.2.1", "source6": "2001:db8::1"},
            "directives": ["juniper_bgp_route"],
        }
    )
    directives = Directives(
        {"juniper_bgp_route": {"name": "BGP Route", "plugins": [], "rules": [], "groups": []}}
    )
    init_user_config(devices=devices, directives=directives)
    query = Query(
        queryLocation="test1",
        queryTarget="192.0.2.0/24",
        queryType="juniper_bgp_route",
    )
    constructor = Construct(device=devices["test1"], query=query)
    assert constructor.target == "192.0.2.0/24"
