from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from ttp import ttp
from oxi.interfaces.contract import Device

if TYPE_CHECKING:
    from oxi.interfaces.contract import Interfaces, System, Vlans


class BaseDevice(ABC):
    _REQUIRED_SECTIONS: frozenset[str] = frozenset({"system", "interfaces", "vlans"})

    def __init__(self, config: str):
        self.config: str = config
        self._loaded_template = self._load_template()
        self._raw: dict = self._run_ttp()

    @property
    @abstractmethod
    def template(self) -> str:
        """
        :return:
        """

    @abstractmethod
    def vlans(self) -> list["Vlans"]: ...

    @abstractmethod
    def interfaces(self) -> list["Interfaces"]: ...

    @abstractmethod
    def system(self) -> "System": ...

    def _load_template(self):
        path = Path(__file__).parent / "template" / self.template
        if not path.exists():
            raise FileNotFoundError(f"Template {self.template} not found")
        return path.read_text(encoding="utf-8")

    def _run_ttp(self) -> dict:
        p = ttp(data=self.config, template=self._loaded_template)
        p.parse()
        raw: dict = p.result()[0][0]
        missing = self._REQUIRED_SECTIONS - raw.keys()
        if missing:
            raise ValueError(
                f"{self.__class__.__name__}: TTP template '{self.template}' "
                f"did not produce required sections: {sorted(missing)}. "
                f"Got: {sorted(raw.keys())}"
            )
        return raw

    def parse(self) -> Device:
        return Device(
            system=self.system(),
            interfaces=self.interfaces(),
            vlans=self.vlans(),
        )
