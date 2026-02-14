from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["routeros", "ros", "mikrotik"])
class Mikrotik(BaseDevice): ...
