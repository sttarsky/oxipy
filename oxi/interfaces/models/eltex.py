from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


def _expand_vlan_range(value: str | list[str]) -> list[str]:
    if isinstance(value, list):
        value = ",".join(str(item) for item in value)

    result: list[str] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" not in part:
            result.append(part)
            continue
        start_s, end_s = part.split("-", 1)
        try:
            start, end = int(start_s), int(end_s)
        except ValueError:
            result.append(part)
            continue
        if start > end:
            start, end = end, start
        result.extend(str(vlan_id) for vlan_id in range(start, end + 1))
    return result


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
            for vid in _expand_vlan_range(ids):
                if vid in named_vlan:
                    continue
                vlans.append({"vlan_id": vid})
        return vlans


if __name__ == "__main__":
    with open("./test_not_found.txt") as file:
        data = file.read()
    eltex = Eltex(data)
    print(eltex.parse())
