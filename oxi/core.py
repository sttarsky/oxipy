from typing import Optional
from requests import Session
from .node import Node


class OxiAPI:
    def __init__(
        self,
        url: str,
        session: Optional[Session] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify: bool = True,
    ):
        self.base_url = url.rstrip("/")
        self._session = session or Session()
        self._session.verify = verify
        if username and password:
            self._session.auth = (username, password)
        self.node = Node(self._session, self.base_url)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._session.close()

    def get(self, endpoint: str, **kwargs) -> dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if not url.endswith(".json"):
            url += ".json"
        result = self._session.get(url, **kwargs)
        if result.status_code == 500:
            raise ValueError(f"page {url} not found")
        return result.json()
