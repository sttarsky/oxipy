from oxi.interfaces import BaseDevice, register_parser


@register_parser(["quasar", "qos"])
class Quasar(BaseDevice):
    template = "quasar.ttp"

    def system(self) -> dict:
        raw = self.raw.get("system", {})
        items = raw if isinstance(raw, list) else [raw]
        selected = next(
            (item for item in items if item.get("assembly_version")),
            items[0] if items else {},
        )
        result = dict(selected)
        result["version"] = (
            result.pop("assembly_version", None)
            or result.pop("engine_version", None)
            or ""
        )
        result.pop("assembly_version", None)
        result.pop("engine_version", None)
        return result

    def interfaces(self) -> list[dict]:
        ether_interfaces: dict = self.raw["interfaces"]
        interfaces: list[dict] = []
        bulk_interfaces: dict = self.raw["bulkinterfaces"]
        for key, value in bulk_interfaces.items():
            interfaces.append(
                {
                    "interface": key,
                    "description": value.get("description"),
                    "ip_address": value.get("ip_address"),
                    "mask": value.get("mask"),
                }
            )
        interfaces.append(ether_interfaces)
        return interfaces


if __name__ == "__main__":
    with open("./test7.txt") as file:
        data = file.read()
    quasar = Quasar(data)
    qt = quasar.parse()
    print(qt)
    print()
    with open("./test8.txt") as file:
        data = file.read()
    quasar = Quasar(data)
    qt = quasar.parse()
    print(qt)
