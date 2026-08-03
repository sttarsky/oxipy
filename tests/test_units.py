import pytest
from conftest import load

from oxi import OxiAPI
from oxi.exception import OxiAPIError
from oxi.interfaces import device_registry
from oxi.interfaces.base import BaseDevice
from oxi.interfaces.models.huawei import Huawei
from oxi.interfaces.models.mikrotik import Mikrotik
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


class TestLineEndingNormalization:
    def test_crlf_and_bare_cr_are_normalized(self):
        text = load("eltex")
        lines = text.splitlines(keepends=True)
        real = ("! \r" + "".join(lines[1:])).replace("\n", "\r\n")

        device = device_registry["eltex"](real)

        assert "system" in device.raw
        assert device.parse().system.version == "6.6.9.3"


class TestNodeNotFound:
    def test_not_found_config_raises_on_parse(self):
        device = device_registry["eltex"](load("eltex", "not_found.conf"), name="HQ")
        assert device.raw is None
        with pytest.raises(OxiAPIError) as exc:
            device.parse()
        assert exc.value.status_code == 404


@pytest.fixture
def clean_registry():
    snapshot = dict(device_registry)
    yield
    device_registry.clear()
    device_registry.update(snapshot)


class TestAddAlias:
    def test_add_alias(self, clean_registry):
        OxiAPI.add_alias("my-vrp", "huawei")
        assert device_registry["my-vrp"] is Huawei
        assert device_registry["my-vrp"] is not Mikrotik

    def test_unknown_model_raises(self, clean_registry):
        with pytest.raises(KeyError, match="not registered"):
            OxiAPI.add_alias("x", "no-such-vendor")
        assert "x" not in device_registry

    def test_alias_list(self, clean_registry):
        OxiAPI.add_alias(["vrp-a", "vrp-b"], "huawei")
        assert device_registry["vrp-a"] is Huawei
        assert device_registry["vrp-b"] is Huawei
