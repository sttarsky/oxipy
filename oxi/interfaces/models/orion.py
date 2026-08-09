from oxi.interfaces import register_parser
from oxi.interfaces.models.ruijie import Ruijie


@register_parser(["orion", "orion networks", "Orion OS", "oos"])
class Orion(Ruijie):
    pass
