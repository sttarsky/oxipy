from oxi.interfaces import BaseDevice, register_parser


@register_parser("h3c")
class H3C(BaseDevice):
    template = "h3c.ttp"

    def vlans(self) -> list[dict]:
        vlan_list = self.raw["vlans"]
        vlans = []
        for item in vlan_list:
            if item.get("vlans_id"):
                vlans.extend([{'vlan_id': vln }for vln in item.get("vlans_id")])
            else:
                vlans.append(item)
        return vlans

if __name__ == "__main__":
    with open("./test5.txt") as file:
        data = file.read()
    h3c = H3C(data)
    print(h3c.parse())