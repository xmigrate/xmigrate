from pydantic import BaseModel


class DiscoverBase(BaseModel):
    project: str
    provider: str
    hosts: list
    username: str
    password: str


class DiscoverCreate(BaseModel):
    project_id: str
    hostname: str
    network: str
    subnet: str
    ports: str | None = None
    cpu_core: int
    cpu_model: str
    ram: str
    disk_details: list
    ip: str


class DiscoverUpdate(DiscoverCreate):
    discover_id: str
    project_id: str | None = None
    class Config:
        orm_mode = True