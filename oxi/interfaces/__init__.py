from typing import Callable, Type

from .base import BaseDevice

device_registry = {}


def register_parser(
    name: list[str] | str,
) -> Callable[[Type[BaseDevice]], Type[BaseDevice]]:
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


from . import models  # noqa: E402, F401

__all__ = ["register_parser", "device_registry", "BaseDevice"]
