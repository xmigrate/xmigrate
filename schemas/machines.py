from pydantic import BaseModel
from typing import Union


class VMCreate(BaseModel):
    blueprint_id: str
    hostname: str
    network: Union[str, None] = None
    ports: Union[str, None] = None
    cpu_core: Union[int, None] = None
    cpu_model: Union[str, None] = None
    ram: Union[str, None] = None


class VMUpdate(VMCreate):
    machine_id: str
    blueprint_id: Union[str, None] = None
    hostname: Union[str, None] = None
    ip: Union[str, None] = None
    ip_created: Union[bool, None] = None
    machine_type: Union[str, None] = None
    public_route: Union[bool, None] = None
    status: Union[str, None] = None
    image_id: Union[str, None] = None
    vm_id: Union[str, None] = None
    nic_id: Union[str, None] = None

    class Config:
        orm_mode = True