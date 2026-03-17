from ipaddress import IPv4Address
from pydantic import BaseModel, ConfigDict, Field


class Base(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class System(BaseModel):
    """
    Required
    """

    model: str
    serial_number: str
    version: str


class Interfaces(Base):
    """
    Required
    """

    name: str = Field(alias="interface")
    ip_address: IPv4Address | None = None
    mask: int | None = None
    description: str | None = None


class Vlans(Base):
    """
    Optional
    """

    vlan_id: int
    name: str | None = Field(default=None, alias="description")


class Device(BaseModel):
    system: System
    interfaces: list[Interfaces]
    vlans: list[Vlans] = []
