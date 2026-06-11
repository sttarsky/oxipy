from requests import HTTPError, Session

from oxi.adapter import OxiAdapter
from oxi.exception import OxiAPIError

from .node import Node


class OxiAPI:
    def __init__(
        self,
        url: str,
        username: str | None = None,
        password: str | None = None,
        verify: bool = True,
    ):
        self.base_url = url.rstrip("/")
        self._session = self.__create_session(username, password, verify)
        self.node = Node(self._session, self.base_url)

    def __create_session(
        self,
        username: str | None = None,
        password: str | None = None,
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
        try:
            reload_response = self._session.get(f"{self.base_url}/reload")
            reload_response.raise_for_status()
        except HTTPError as e:
            raise OxiAPIError.from_http_error(e, context="Reload Oxidized") from e
        return reload_response.status_code
