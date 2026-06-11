from oxi.interfaces import BaseDevice, register_parser


@register_parser(["quasar", "qos"])
class Quasar(BaseDevice):
    template = "quasar.ttp"

    def interfaces(self) -> list[dict]:
        ether_interface: dict = self.raw.get("interfaces", {})
        interfaces: list[dict] = []
        bulk_interfaces: dict = self.raw.get("bulkinterfaces", {})
        for key, value in bulk_interfaces.items():
            interfaces.append(
                {
                    "interface": key,
                    "description": value.get("description"),
                    "ip_address": value.get("ip_address"),
                    "mask": value.get("mask"),
                }
            )
        if ether_interface:
            interfaces.append(ether_interface)
        return interfaces
