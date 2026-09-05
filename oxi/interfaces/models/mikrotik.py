from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["routeros", "ros", "mikrotik"])
class Mikrotik(BaseDevice):
    template = "mikrotik.ttp"

    def vlans(self):
        return self.raw.get("vlans", [])
