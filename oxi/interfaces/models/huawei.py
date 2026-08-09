from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["vrp", "huawei"])
class Huawei(BaseDevice):
    template = "huawei.ttp"

    def vlans(self) -> list[dict]:
        result: list[dict] = []
        for vlan in self.raw.get("vlans"):
            result.extend({"vlan_id": _vl} for _vl in vlan.get("vlan_ids", []))
        return result
