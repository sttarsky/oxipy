from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice
from oxi.interfaces.utils import expand_vlan_range


@register_parser(["QTECH"])
class Qtech(BaseDevice):
    template = "qtech.ttp"

    def vlans(self) -> list[dict]:
        vlans_ttp = self.raw.get("vlans", [])
        vlans: list[dict] = []
        named_vlan: set[str] = set()
        for item in vlans_ttp:
            vlan_id = item.get("vlan_id")
            if vlan_id and "," not in vlan_id and "-" not in vlan_id:
                named_vlan.add(vlan_id)
                vlans.append(item)
                continue

            ids = item.get("vlan_ids") or vlan_id or ""
            tail = item.get("vlan_tail")
            if tail:
                ids = [*ids, tail] if isinstance(ids, list) else f"{ids},{tail}"
            for vid in expand_vlan_range(ids):
                if vid in named_vlan:
                    continue
                vlans.append({"vlan_id": vid})
        return vlans
