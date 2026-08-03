from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["vrp", "huawei"])
class Huawei(BaseDevice):
    template = "huawei.ttp"

    def vlans(self) -> list[dict]:
        vlans = self.raw.get("vlans", {})
        if isinstance(vlans, list):
            result = []
            for vlan in vlans:
                result.extend([{"vlan_id": _vl} for _vl in vlan.get("vlan_ids", [])])
            return result
        else:
            return [{"vlan_id": vlan} for vlan in vlans.get("vlan_ids", [])]
