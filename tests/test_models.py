import json

import pytest

from conftest import FIXTURES, load
from oxi.interfaces import device_registry

MODEL_CASES = [
    ("mikrotik", "config.conf", "config.expected.json"),
    ("keenetic", "config.conf", "config.expected.json"),
    ("qtech", "config_1.conf", "config_1.expected.json"),
    ("qtech", "config_2.conf", "config_2.expected.json"),
    ("huawei", "config.conf", "config.expected.json"),
    ("eltex", "config.conf", "config.expected.json"),
    ("quasar", "config_1.conf", "config_1.expected.json"),
    ("quasar", "config_2.conf", "config_2.expected.json"),
]


@pytest.mark.parametrize("model_key, fixture, expected_file", MODEL_CASES)
def test_parse_matches_golden(model_key, fixture, expected_file):
    cls = device_registry[model_key]
    raw = load(model_key, fixture)

    parsed = cls(raw).parse().model_dump(by_alias=True, mode="json")

    expected = json.loads((FIXTURES / model_key / expected_file).read_text("utf-8"))
    assert parsed == expected


@pytest.mark.parametrize("model_key, fixture, _expected", MODEL_CASES)
def test_parse_has_required_sections(model_key, fixture, _expected):
    cls = device_registry[model_key]
    device = cls(load(model_key, fixture)).parse()

    assert device.system is not None
    assert isinstance(device.interfaces, list)
    assert isinstance(device.vlans, list)
