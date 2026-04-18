from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


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
        vlans = []
        named_vlan = set()
        for item in vlans_ttp:
            if item.get("vlan_id"):
                named_vlan.add(item.get("vlan_id"))
                vlans.append(item)
            else:
                ids = item.get("vlan_ids", "")
                tail = item.get("vlan_tail")
                if tail:
                    ids = f"{ids},{tail}"
                for vid in ids:
                    vid = vid.strip()
                    if vid in named_vlan:
                        continue
                    vlans.append({"vlan_id": vid})
        return vlans


if __name__ == "__main__":
    with open("./test_not_found.txt") as file:
        data = file.read()
    eltex = Eltex(data)
    print(eltex.parse())
