from ipaddress import ip_interface
from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice
from oxi.interfaces.utils import decode_utf


@register_parser(["NDMS", "keenetic", "KeeneticOS"])
class Keenetic(BaseDevice):
    template = "keenetic.ttp"

    def interfaces(self):
        interfaces: list[dict] = self.raw["interfaces"]
        for item in interfaces:
            if item.get("ip_address") and item.get("netmask"):
                ipaddress = ip_interface(
                    f"{item.get('ip_address')}/{item.get('netmask')}"
                )
                item["mask"] = ipaddress.network.prefixlen
                item.pop("netmask", "Key not found")
            if item.get("description"):
                decoded = decode_utf(item.get("description", ""))
                item["description"] = decoded
        return interfaces

    def vlans(self):
        vlans = self.raw["vlans"]
        for item in vlans:
            if item.get("description"):
                decoded = decode_utf(item.get("description", ""))
                item["description"] = decoded
        return vlans
