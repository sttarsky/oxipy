from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["NDMS", "keenetic", "KeeneticOS"])
class Keenetic(BaseDevice):
    template = "keenetic.ttp"

    def system(self): ...

    def interfaces(self): ...

    def vlans(self): ...


if __name__ == "__main__":
    with open("../../test2.txt") as file:
        data = file.read()
    mikr = Keenetic(data)
    print(mikr.parse().json())
