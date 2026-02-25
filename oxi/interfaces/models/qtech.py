from oxi.interfaces import register_parser
from oxi.interfaces.base import BaseDevice


@register_parser(["QTECH"])
class Qtech(BaseDevice):
    template = "qtech.ttp"
