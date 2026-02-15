from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["routeros", "ros", "mikrotik"])
class Mikrotik(BaseDevice):
    template = "mikrotik.ttp"


if __name__ == "__main__":
    mikr = Mikrotik()
    mikr.run()
    print(mikr.load)
