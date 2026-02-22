import os
from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["routeros", "ros", "mikrotik"])
class Mikrotik(BaseDevice):
    template = "mikrotik.ttp"

    # def system(self) -> "System":
    #     systems = self._raw.get("system")
    #     return System(**systems)

    # def interfaces(self) -> "Interfaces":
    #     return [Interfaces(**item) for item in self._raw.get("interfaces")]

    # def vlans(self) -> list["Vlans"]:
    #     return [Vlans(**item) for item in self._raw.get("vlans")]


if __name__ == "__main__":
    print(os.path.abspath(os.curdir))
    with open("./test.txt") as file:
        data = file.read()
    mikr = Mikrotik(data)
    print(mikr.parse().json())
