from functools import cached_property
import json
from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel

from .interfaces import BaseDevice, device_registry

if TYPE_CHECKING:
    from requests import Session

TModel = TypeVar("TModel", bound=BaseModel)


class ModelView(Generic[TModel]):
    def __init__(self, model: TModel | list[TModel]):
        self._model = model

    def json(self) -> str:
        if isinstance(self._model, list):
            return json.dumps(
                [item.model_dump(by_alias=True) for item in self._model],
                ensure_ascii=False,
            )
        return self._model.model_dump_json(by_alias=True)

    def __getattr__(self, item):
        return getattr(self._model, item)

    def __repr__(self) -> str:
        return repr(self._model)


class NodeConfig:
    def __init__(self, session: "Session", full_name: str, model: str, base_url: str):
        self._session = session
        self._full_name = full_name
        self._model = model.lower()
        self._url = f"{base_url}/node/fetch/{full_name}"
        self._device: type[BaseDevice] = device_registry.get(self._model.lower())
        if self._device is None:
            raise ValueError(f"Device model '{self._model}' not found in registry")
        self._parsed_data = self._device(self.text).parse()

    @cached_property
    def _response(self):
        response = self._session.get(self._url)
        response.raise_for_status()
        return response

    @property
    def text(self):
        return self._response.text

    def json(self):
        return self._parsed_data.model_dump_json()

    def __str__(self):
        return self.text

    @property
    def vlans(self):
        return ModelView(self._parsed_data.vlans)

    @property
    def interfaces(self):
        return ModelView(self._parsed_data.interfaces)

    @property
    def system(self):
        return ModelView(self._parsed_data.system)
