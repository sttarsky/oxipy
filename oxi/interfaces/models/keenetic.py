from ipaddress import ip_interface
from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice
from oxi.interfaces.contract import Interfaces, Vlans


@register_parser(["NDMS", "keenetic", "KeeneticOS"])
class Keenetic(BaseDevice):
    template = "keenetic.ttp"

    def _decode_utf(self, text: str):
        if "\\x" in text:
            desc = text.strip('"')
            decoded = (
                desc.encode("utf-8")
                .decode("unicode_escape")
                .encode("latin1")
                .decode("utf-8")
            )
            return decoded
        return text

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
                decoded = self._decode_utf(item.get("description", ""))
                item["description"] = decoded
        return interfaces

    def vlans(self):
        vlans = self.raw["vlans"]
        for item in vlans:
            if item.get("description"):
                decoded = self._decode_utf(item.get("description", ""))
                item["description"] = decoded
        return vlans


if __name__ == "__main__":
    with open("./test2.txt") as file:
        data = file.read()
    mikr = Keenetic(data)
    print(mikr.parse().model_dump_json())
