from typing import Callable, Type

from .base import BaseDevice

device_registry = {}


def register_parser(
    name: list[str],
) -> Callable[[Type[BaseDevice]], Type[BaseDevice]]:
    def wrapper(cls):
        for item in name:
            device_registry[item.lower()] = cls
        return cls

    return wrapper


from . import models  # noqa: E402, F401

__all__ = ["register_parser", "device_registry"]
