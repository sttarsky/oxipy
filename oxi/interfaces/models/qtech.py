import os
from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["QTECH"])
class Qtech(BaseDevice):
    template = "qtech.ttp"

    def system(self) -> dict:
        system = self.raw["system"]
        return system

    def vlans(self) -> list[dict]:
        vlans_ttp = self.raw["vlans"]
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
                for vid in ids.split(","):
                    vid = vid.strip()
                    if vid in named_vlan:
                        continue
                    vlans.append({"vlan_id": vid})
        return vlans


if __name__ == "__main__":
    print(os.path.abspath(os.curdir))
    with open("./test3.txt") as file:
        data = file.read()
    qtech = Qtech(data)
    qt = qtech.parse()
    print(qt)
