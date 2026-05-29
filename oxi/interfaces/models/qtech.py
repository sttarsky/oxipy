from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


def _expand_vlan_range(value: str | list[str]) -> list[str]:
    """Expand values like '1,7,14-15' into individual VLAN IDs."""
    if isinstance(value, list):
        value = ",".join(str(item) for item in value)

    result: list[str] = []
    if not value:
        return result
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            try:
                start, end = int(start_s), int(end_s)
            except ValueError:
                result.append(part)
                continue
            if start > end:
                start, end = end, start
            result.extend(str(i) for i in range(start, end + 1))
        else:
            result.append(part)
    return result


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
            for vid in _expand_vlan_range(ids):
                if vid in named_vlan:
                    continue
                vlans.append({"vlan_id": vid})
        return vlans


if __name__ == "__main__":
    with open("./test3.txt") as file:
        data = file.read()
    qtech = Qtech(data)
    qt = qtech.parse()
    print(qt)
    with open("./test3-1.txt") as file:
        data = file.read()
    qtech = Qtech(data)
    qt = qtech.parse()
    print(qt)
