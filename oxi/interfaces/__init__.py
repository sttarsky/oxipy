from collections.abc import Callable

from oxi.exception import UnknownModelError

from .base import BaseDevice

device_registry = {}


def register_parser(
    name: list[str] | str,
) -> Callable[[type[BaseDevice]], type[BaseDevice]]:
    def wrapper(cls):
        name_list = []
        if isinstance(name, str):
            name_list.append(name)
        else:
            name_list.extend(name)
        for item in name_list:
            device_registry[item.lower()] = cls
        return cls

    return wrapper


def add_alias(alias: str | list[str], model: str) -> None:
    cls = device_registry.get(model.lower())
    if cls is None:
        raise UnknownModelError(
            f"Model '{model}' is not registered. Available: {sorted(device_registry)}"
        )
    register_parser(alias)(cls)


from . import models  # noqa: E402, F401

__all__ = ["register_parser", "add_alias", "device_registry", "BaseDevice"]
