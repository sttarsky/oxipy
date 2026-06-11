from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["vrp", "huawei"])
class Huawei(BaseDevice):
    template = "huawei.ttp"

    def vlans(self) -> list[dict]:
        vlan_ids = self.raw.get("vlans", {}).get("vlan_ids", [])
        return [{"vlan_id": vlan} for vlan in vlan_ids]
