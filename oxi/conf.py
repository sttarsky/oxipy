from functools import cached_property
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from requests import Session


class NodeConfig:
    def __init__(self, session: "Session", full_name: str, model: str, base_url: str):
        self._session = session
        self._full_name = full_name
        self._model = model
        self._url = f"{base_url}/node/fetch/{full_name}"
        self._device: type[BaseDevice] = device_registry.get(self._model.lower())
        if self._device is None:
            raise ValueError(f"Device model '{self._model}' not found in registry")
        self._parsed_data = self._device(self.text).parse_config()

    @cached_property
    def _response(self):
        log.debug(f"Fetching config from {self._url}")
        response = self._session.get(self._url)
        response.raise_for_status()
        return response

    @property
    def text(self):
        return self._response.text

    @property
    def json(self):
        return self._response.json()

    def __str__(self):
        return self.text

    def vlans(self):
        return self._parsed_data.vlans

    def l3interfaces(self):
        return self._parsed_data.l3interfaces

    def vlaninterfaces(self):
        return self._parsed_data.vlaninterfaces
