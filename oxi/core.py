from typing import Optional
from requests import Session
from .node import Node


# TODO: Add custom adapter for Oxi
class OxiAPI:
    def __init__(
        self,
        url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify: bool = True,
    ):
        self.base_url = url.rstrip("/")
        self._session = Session()
        self._session.verify = verify
        if username is not None and password is not None:
            self._session.auth = (username, password)
        self.node = Node(self._session, self.base_url)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        return self._session.close()

    def reload(self):
        reload_response = self._session.get(f"{self.base_url}/reload")
        reload_response.raise_for_status()
        return reload_response.status_code
