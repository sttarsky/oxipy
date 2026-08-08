from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["RUJIE", "RGOS", "ruijie networks"])
class Ruijie(BaseDevice):
    template = "ruijie.ttp"
