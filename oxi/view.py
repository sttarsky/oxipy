from functools import cached_property
from typing import TYPE_CHECKING

from .conf import NodeConfig


if TYPE_CHECKING:
    from requests import Session


class NodeView:
    def __init__(self, session: "Session", base_url: str, data: dict):
        self._session = session
        self._base_url = base_url
        self._data = data

    @property
    def ip(self):
        return self._data.get("ip")

    @property
    def full_name(self):
        return self._data.get("full_name")

    @property
    def group(self):
        return self._data.get("group")

    @property
    def model(self):
        return self._data.get("model")

    @cached_property
    def config(self):
        return NodeConfig(self._session, self.full_name, self.model, self._base_url)
