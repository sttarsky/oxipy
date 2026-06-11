from oxi.interfaces import BaseDevice, register_parser


@register_parser("h3c")
class H3C(BaseDevice):
    template = "h3c.ttp"

    def vlans(self) -> list[dict]:
        vlan_list = self.raw.get("vlans", [])
        vlans: list[dict] = []
        for item in vlan_list:
            vlan_ids = item.get("vlans_id")
            if not vlan_ids:
                vlans.append(item)
                continue
            vlans.extend({"vlan_id": vlan_id} for vlan_id in vlan_ids)
        return vlans