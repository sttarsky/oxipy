from typing import Optional
from requests import Session

from oxi.adapter import OxiAdapter
from .node import Node


class OxiAPI:
    def __init__(
        self,
        url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify: bool = True,
    ):
        self.base_url = url.rstrip("/")
        self._session = self.__create_session(username, password, verify)
        self.node = Node(self._session, self.base_url)

    def __create_session(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify: bool = True,
    ) -> Session:
        session = Session()
        adapter = OxiAdapter(timeout=10, max_retries=3)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.verify = verify
        if username and password:
            session.auth = (username, password)
        return session

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
