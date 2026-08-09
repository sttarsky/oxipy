import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from oxi.interfaces import device_registry

TEMPLATES_DIR = (
    Path(__file__).parent.parent / "oxi" / "interfaces" / "models" / "templates"
)

# Groups that must map to a list. TTP collapses a single match into a dict,
# so these groups have to use the `*` path formatter to always emit a list.
LIST_GROUPS = frozenset({"interfaces", "vlans"})


def _group_names(text: str) -> list[str]:
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        root = ET.fromstring(f"<template>{text}</template>")
    return [g.get("name") for g in root.iter("group") if g.get("name")]


@pytest.mark.parametrize(
    "template", sorted(TEMPLATES_DIR.glob("*.ttp")), ids=lambda p: p.name
)
def test_list_groups_use_star_formatter(template):
    """interfaces/vlans groups must force list output with the `*` formatter."""
    for name in _group_names(template.read_text(encoding="utf-8")):
        base = name.rstrip("*").split(".")[0]
        if base in LIST_GROUPS:
            assert name.endswith("*"), (
                f"{template.name}: group '{name}' must use the '*' path "
                f"formatter so TTP always returns a list, even for a single match"
            )


RUIJIE_SINGLE_VLAN = """\
! System description      : Test Switch(S1234) By Ruijie Networks
! System software version : S_RGOS 11.0(1)
! System serial number    : SN123
!
vlan 10
 name MGMT
!
interface TenGigabitEthernet 1/0/1
 description uplink
!
"""


def test_single_named_vlan_and_interface_return_lists():
    """A config with exactly one named VLAN/interface must not collapse to a dict."""
    device = device_registry["ruijie"](RUIJIE_SINGLE_VLAN)

    assert isinstance(device.raw["vlans"], list)
    assert isinstance(device.raw["interfaces"], list)

    parsed = device.parse()
    assert [(v.vlan_id, v.name) for v in parsed.vlans] == [(10, "MGMT")]
    assert len(parsed.interfaces) == 1
