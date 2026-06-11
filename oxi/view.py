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

    def _updater(self) -> int:
        response = self._session.get(f"{self._base_url}/node/next/{self.full_name}")
        response.raise_for_status()
        return response.status_code

    @property
    def name(self) -> str:
        return self._data.get("name")

    @property
    def ip(self) -> str:
        return self._data.get("ip")

    @property
    def full_name(self) -> str:
        return self._data.get("full_name")

    @property
    def group(self) -> str:
        return self._data.get("group")

    @property
    def model(self) -> str:
        return self._data.get("model")

    @property
    def last_status(self) -> str:
        last = self._data.get("last") or {}
        return last.get("status")

    @property
    def last_check(self) -> str:
        last = self._data.get("last") or {}
        return last.get("start")

    def refresh(self) -> str:
        result = self._updater()
        if result != 200:
            raise ValueError(f"Failed to refresh node {self.full_name}")
        return "OK"

    @cached_property
    def config(self) -> NodeConfig:
        return NodeConfig(self._session, self.full_name, self.model, self._base_url)
