from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxi.interfaces.contract import Interfaces, System, Vlans


class BaseDevice(ABC):
    @property
    @abstractmethod
    def template(self) -> str:
        """
        :return:
        """

    @abstractmethod
    def vlans(self) -> "Vlans": ...

    @abstractmethod
    def interfaces(self) -> "Interfaces": ...

    @abstractmethod
    def system(self) -> "System": ...

    def __load_template(self):
        path = Path(__file__).parent / "template" / self.template
        if not path.exists():
            raise FileNotFoundError(f"Template {self.template} not found")
        return path.read_text(encoding="utf-8")

    def run(self):
        self.load = self.__load_template()
        return self.load


BaseDevice()
