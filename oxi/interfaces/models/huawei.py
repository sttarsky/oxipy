from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["vrp", "huawei"])
class Huawei(BaseDevice):
    template = "huawei.ttp"

    def vlans(self) -> list[dict]:
        vlan_ids = self.raw.get("vlans", {}).get("vlan_ids", [])
        return [{"vlan_id": vlan} for vlan in vlan_ids]


if __name__ == "__main__":
    with open("./test4.txt") as file:
        data = file.read()
    huawei = Huawei(data)
    print(huawei.parse())
