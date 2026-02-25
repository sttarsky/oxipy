import os
from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["routeros", "ros", "mikrotik"])
class Mikrotik(BaseDevice):
    template = "mikrotik.ttp"


if __name__ == "__main__":
    print(os.path.abspath(os.curdir))
    with open("./test.txt") as file:
        data = file.read()
    mikr = Mikrotik(data)
    print(mikr.parse().json())
