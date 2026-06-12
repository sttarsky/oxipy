from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice
from oxi.interfaces.utils import expand_vlan_range


@register_parser("eltex")
class Eltex(BaseDevice):
    template = "eltex.ttp"

    def system(self) -> dict:
        system = self.raw["system"]
        serial_num = self.raw["serial"]
        if serial_num:
            if len(serial_num) > 1:
                serial_num = serial_num[0]
            system["serial_number"] = serial_num.get("serial_number")
        return system

    def vlans(self) -> list[dict]:
        vlans_ttp = self.raw.get("vlans", [])
        vlans: list[dict] = []
        named_vlan: set[str] = set()
        for item in vlans_ttp:
            vlan_id = item.get("vlan_id")
            if vlan_id:
                named_vlan.add(str(vlan_id))
                vlans.append(item)
                continue

            ids = item.get("vlan_ids", "")
            tail = item.get("vlan_tail")
            if tail:
                ids = [*ids, tail] if isinstance(ids, list) else f"{ids},{tail}"
            for vid in expand_vlan_range(ids):
                if vid in named_vlan:
                    continue
                vlans.append({"vlan_id": vid})
        return vlans
