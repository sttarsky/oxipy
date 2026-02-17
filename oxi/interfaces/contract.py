from ipaddress import IPv4Address
from pydantic import BaseModel, Field


class Interfaces(BaseModel):
    name: str
    ip_address: IPv4Address | None = None
    mask: int | None = None
    description: str


class System(BaseModel):
    model: str
    serial_number: str
    version: str


class Vlans(BaseModel):
    id: int
    name: str | None = Field(default=None, alias="description")


class Device(BaseModel):
    system: System
    interfaces: list[Interfaces] = []
    vlans: list[Vlans] = []
