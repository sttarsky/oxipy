from ipaddress import IPv4Address
from pydantic import BaseModel, ConfigDict, Field


class Interfaces(BaseModel):
    name: str
    ip_address: IPv4Address | None = None
    mask: int | None = None
    description: str | None = None


class System(BaseModel):
    model: str
    serial_number: str
    version: str


class Vlans(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vlan_id: int
    name: str | None = Field(default=None, alias="description")


class Device(BaseModel):
    system: System
    interfaces: list[Interfaces] = []
    vlans: list[Vlans] = []
