from oxi.interfaces import BaseDevice, register_parser


@register_parser(["quasar", "qos"])
class Quasar(BaseDevice):
    template = "quasar.ttp"

    def interfaces(self) -> list[dict]:
        inter = self.raw["interfaces"]
        # test = self.raw["mass"]
        print(inter)
        # print(test)
        return inter


if __name__ == "__main__":
    with open("./test7.txt") as file:
        data = file.read()
    quasar = Quasar(data)
    qt = quasar.parse()
    print(qt)
