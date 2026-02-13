from typing import TYPE_CHECKING

from oxi.view import NodeView


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
        if response.status_code == 500:
            log.warning(
                "Oxidized response: %r , %r not found", response.status_code, url
            )
            raise ValueError(f"page {url} not found")
        return NodeView(
            session=self._session, base_url=self._base_url, data=response.json()
        )
