import pytest

from conftest import load
from oxi.exception import OxiAPIError
from oxi.interfaces import device_registry
from oxi.interfaces.base import BaseDevice
from oxi.interfaces.contract import Interfaces, System
from oxi.interfaces.utils import decode_utf, expand_vlan_range


class TestExpandVlanRange:
    @pytest.mark.parametrize("expand", [expand_vlan_range])
    def test_simple_and_range(self, expand):
        assert expand("1,7,14-15") == ["1", "7", "14", "15"]

    @pytest.mark.parametrize("expand", [expand_vlan_range])
    def test_reversed_range_is_normalized(self, expand):
        assert expand("15-13") == ["13", "14", "15"]

    @pytest.mark.parametrize("expand", [expand_vlan_range])
    def test_non_numeric_range_kept_verbatim(self, expand):
        assert expand("a-b") == ["a-b"]

    @pytest.mark.parametrize("expand", [expand_vlan_range])
    def test_empty(self, expand):
        assert expand("") == []

    @pytest.mark.parametrize("expand", [expand_vlan_range])
    def test_list_input(self, expand):
        assert expand(["1", "3-4"]) == ["1", "3", "4"]


class TestDecodeUtf:
    def test_plain_text_passthrough(self):
        assert decode_utf("Plain ASCII") == "Plain ASCII"

    def test_escaped_utf8_is_decoded(self):
        assert decode_utf(r'"\xd0\x94\xd0\xbe\xd0\xbc"') == "Дом"


class TestTemplateValidation:
    def test_missing_required_group_raises(self):
        class OnlySystem(BaseDevice):
            template = "dummy.ttp"

            def _load_template(self):
                return '<group name="system"></group>'

        with pytest.raises(ValueError, match="missing required groups"):
            OnlySystem("data")

    def test_missing_template_file_raises(self):
        class NoTemplate(BaseDevice):
            template = "does_not_exist.ttp"

        with pytest.raises(FileNotFoundError):
            NoTemplate("data")


class TestNodeNotFound:
    def test_not_found_config_raises_on_parse(self):
        device = device_registry["eltex"](load("eltex", "not_found.conf"), name="HQ")
        assert device.raw is None
        with pytest.raises(OxiAPIError) as exc:
            device.parse()
        assert exc.value.status_code == 404
