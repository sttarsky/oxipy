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
    def vlans(self) -> list["Vlans"]:
        f"""
        Parse VLAN configuration from self._raw['vlans'].

        Expected raw structure:
            [{"id": 10, "description": "MGMT"}, {"id": 15, "name": "SSH"}, ...]

        Returns:
            list[Vlans]: список VLAN из секции vlans,
                пустой список если секция отсутствует.

        Raises:
            ValueError: если _raw содержит некорректные данные.
        """
        ...

    @abstractmethod
    def interfaces(self) -> list["Interfaces"]:
        f"""
        Parse Interface configuration from self._raw['interfaces'].

        Expected raw structure:
            [{"name": "GEthernet1/0/1", "ip_address": "192.168.1.1", "mask": "24", "description": "IPBB interface"}]
        
        Raises:
            ValueError: если _raw содержит некорректные данные.
        """
        ...

    @abstractmethod
    def system(self) -> "System":
        """
        Parse System configuration from self._raw['system'].

        Expected raw structure:
            {"model":"RB951Ui-2nD", serial_number: "B88C0B31117B", "version": "7.12.1"}

        Raises:
            ValueError: если _raw содержит некорректные данные.
        """
        ...

    def _load_template(self):
        path = Path(__file__).parent / "models" / "templates" / self.template
        if not path.exists():
            print("-" * 12)
            print(path)
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
