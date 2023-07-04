from pydantic import BaseModel


class VMCreate(BaseModel):
    blueprint_id: str
    hostname: str
    network: str | None = None
    ports: str | None = None
    cpu_core: int | None = None
    cpu_model: str | None = None
    ram: str | None = None


class VMUpdate(VMCreate):
    machine_id: str
    blueprint_id: str | None = None
    hostname: str | None = None
    ip: str | None = None
    ip_created: bool | None = None
    machine_type: str | None = None
    public_route: bool | None = None
    status: str | None = None
    image_id: str | None = None
    vm_id: str | None = None
    nic_id: str | None = None

    class Config:
        orm_mode = True