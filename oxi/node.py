from typing import TYPE_CHECKING

from .view import NodeView


if TYPE_CHECKING:
    from requests import Session


class Node:
    def __init__(self, session: "Session", base_url: str):
        self._session = session
        self._base_url = base_url
        self._data = None

    def __call__(self, name: str) -> NodeView:
        url = f"{self._base_url}/node/show/{name}"
        if not url.endswith(".json"):
            url += ".json"
        response = self._session.get(url)
        response.raise_for_status()
        return NodeView(
            session=self._session, base_url=self._base_url, data=response.json()
        )
