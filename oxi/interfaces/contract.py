from ipaddress import IPv4Address
from pydantic import BaseModel, Field


class Interfaces(BaseModel):
    ip_address: IPv4Address
    mask: int
    description: str


class System(BaseModel):
    model: str
    serial_number: str
    version: str


class Vlans(BaseModel):
    id: int
    name: str = Field(alias="description")


class Device(BaseModel):
    system: System
    interfaces: Interfaces
    vlans: Vlans
