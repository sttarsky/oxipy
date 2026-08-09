from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["ruijie networks", "ruijie", "rgos"])
class Ruijie(BaseDevice):
    template = "ruijie.ttp"

    def vlans(self) -> list[dict]:
        ranges: list[dict] = []
        named: list[dict] = []
        for vlan in self.raw.get("vlans"):
            if vlan.get("vlan_ids") is not None:
                ranges.extend({"vlan_id": _vl} for _vl in vlan["vlan_ids"])
            elif vlan.get("vlan_id") is not None:
                named.append(
                    {"vlan_id": vlan["vlan_id"], "description": vlan.get("name")}
                )
        return ranges + named
