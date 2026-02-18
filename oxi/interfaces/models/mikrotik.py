import re
from typing import TYPE_CHECKING
from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice

if TYPE_CHECKING:
    from oxi.interfaces.contract import Interfaces, System, Vlans


@register_parser(["routeros", "ros", "mikrotik"])
class Mikrotik(BaseDevice):
    template = "mikrotik.ttp"

    def system(self) -> "System":
        print(self._raw["system"])
        print("-" * 12)

    def interfaces(self) -> "Interfaces":
        print(f"{self._raw["interfaces"]=}")
        print("-" * 12)

    def vlans(self) -> list["Vlans"]:
        raw = self._raw.get("vlans", [])
        print(raw)


if __name__ == "__main__":
    with open("../../test.txt") as file:
        data = file.read()
    mikr = Mikrotik(data)
    mikr.parse()
    print(mikr.load)
