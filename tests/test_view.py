import json
from ipaddress import IPv4Address

import pytest

from oxi.conf import ModelView
from oxi.interfaces.contract import Interfaces, System


@pytest.fixture
def system_view():
    system = System(model="RB951", serial_number="ABC123", version="7.12")
    return ModelView(system)


@pytest.fixture
def interfaces_view():
    items = [
        Interfaces(interface="eth0", ip_address="192.168.1.1", mask=24),
        Interfaces(interface="eth1", description="uplink"),
    ]
    return ModelView(items)


class TestSingleModelView:
    def test_attribute_proxy(self, system_view):
        assert system_view.model == "RB951"
        assert system_view.serial_number == "ABC123"

    def test_dump(self, system_view):
        assert system_view.dump() == {
            "model": "RB951",
            "serial_number": "ABC123",
            "version": "7.12",
        }

    def test_dump_json(self, system_view):
        assert json.loads(system_view.dump_json())["model"] == "RB951"

    def test_iter_raises(self, system_view):
        with pytest.raises(TypeError):
            iter(system_view)

    def test_len_raises(self, system_view):
        with pytest.raises(TypeError):
            len(system_view)

    def test_getitem_raises(self, system_view):
        with pytest.raises(TypeError):
            system_view[0]


class TestListModelView:
    def test_len(self, interfaces_view):
        assert len(interfaces_view) == 2

    def test_iter(self, interfaces_view):
        names = [iface.name for iface in interfaces_view]
        assert names == ["eth0", "eth1"]

    def test_getitem(self, interfaces_view):
        assert interfaces_view[0].name == "eth0"

    def test_slice(self, interfaces_view):
        assert len(interfaces_view[:1]) == 1

    def test_dump_uses_aliases(self, interfaces_view):
        dumped = interfaces_view.dump()
        assert dumped[0]["interface"] == "eth0"
        assert dumped[0]["ip_address"] == IPv4Address("192.168.1.1")

    def test_dump_json(self, interfaces_view):
        assert interfaces_view.dump_json()

    def test_dump_json_keeps_unicode(self):
        view = ModelView([Interfaces(interface="eth0", description="Дом")])
        assert "Дом" in view.dump_json()
