from abc import ABC, abstractmethod
from pathlib import Path
from ttp import ttp
from oxi.interfaces.contract import Device
import xml.etree.ElementTree as ET
from oxi.interfaces.contract import Interfaces, System, Vlans


class BaseDevice(ABC):
    _REQUIRED_SECTIONS: frozenset[str] = frozenset({"system", "interfaces"})
    _OPTIONAL_SECTIONS: frozenset[str] = frozenset({"vlans"})

    def __init__(self, config: str):
        self.config: str = config

        self._loaded_template = self._load_template()
        self._declared_sections = None
        self._validate_template_groups()
        self.raw: dict = self._run_ttp()

    @property
    @abstractmethod
    def template(self) -> str:
        """
        Expected structure:
            Название файла с парсером ttp
        Returns:
            None
        """

    def vlans(self) -> list[dict]:
        """
        Parse VLAN configuration from self.raw['vlans'].

        Expected structure:
            [{"id": 10, "description": "MGMT"}, {"id": 15, "name": "SSH"}, ...]

        Returns:
            list[Vlans]: список VLAN из секции vlans,
                пустой список если секция отсутствует.

        Raises:
            ValueError: если raw содержит некорректные данные.
        """
        return self.raw.get("vlans", [])

    def interfaces(self) -> list[dict]:
        """
        Parse Interface configuration from self.raw['interfaces'].

        Expected raw structure:
            [{"name": "GEthernet1/0/1", "ip_address": "192.168.1.1", "mask": "24", "description": "IPBB interface"}]

        Raises:
            ValueError: если raw содержит некорректные данные.
        """
        return self.raw.get("interfaces", [])

    def system(self) -> dict:
        """
        Parse System configuration from self.raw['system'].

        Expected raw structure:
            {"model":"RB951Ui-2nD", serial_number: "B88C0B31117B", "version": "7.12.1"}

        Raises:
            ValueError: если raw содержит некорректные данные.
        """
        return self.raw.get("system", None)

    def _validate_contract(self) -> dict:
        system_data = self.system()
        interfaces_data = self.interfaces() or []
        result = {
            "system": System(**system_data),
            "interfaces": [Interfaces(**item) for item in interfaces_data],
            "vlans": [],
        }

        if "vlans" in self._declared_sections:
            if "vlans" not in self.raw:
                raise ValueError(
                    f"{self.__class__.__name__}: template '{self.template}' declares optional group "
                    f"'vlans', but TTP did not return it."
                )
            vlans_data = self.vlans() or []
            result["vlans"] = [Vlans(**item) for item in vlans_data]
        return result

    def _load_template(self):
        """Подгрузка темплейтов из папки models/templates"""
        path = Path(__file__).parent / "models" / "templates" / self.template
        if not path.exists():
            raise FileNotFoundError(f"Template {self.template} not found")
        return path.read_text(encoding="utf-8")

    def _validate_template_groups(self) -> None:
        """Проверяем только обязательные группы в template."""
        try:
            root = ET.fromstring(self._loaded_template)
        except ET.ParseError:
            root = ET.fromstring(f"<template>{self._loaded_template}</template>")

        declared = {g.get("name") for g in root.iter("group") if g.get("name")}
        self._declared_sections = declared

        missing_required = self._REQUIRED_SECTIONS - declared
        if missing_required:
            raise ValueError(
                f"{self.__class__.__name__}: template '{self.template}' "
                f"missing required groups: {sorted(missing_required)}. "
                f"Declared groups: {sorted(declared)}"
            )

    def _run_ttp(self) -> dict:
        """Основной парсер"""
        p = ttp(data=self.config, template=self._loaded_template)
        p.parse()
        raw: dict = p.result()[0][0]
        missing = self._REQUIRED_SECTIONS - raw.keys()
        if missing:
            raise ValueError(
                f"{self.__class__.__name__}: TTP template '{self.template}' "
                f"did not produce required groups: {sorted(missing)}. "
                f"Return only: {(raw.keys())}"
            )
        return raw

    def parse(self) -> Device:
        return Device(**self._validate_contract())
