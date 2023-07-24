from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Union


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
    ports: Union[str, None] = None
    cpu_core: int
    cpu_model: str
    ram: str
    disk_details: list
    ip: str


class DiscoverUpdate(BaseModel):
    id: str = Field(alias='discover_id')
    hostname: str
    network: str
    subnet: str
    ports: Optional[str] = None
    cpu_core: int
    cpu_model: str
    ram: str
    disk_details: list
    ip: str
    updated_at: datetime = Field(default_factory=datetime.now())

    class Config:
        allow_population_by_field_name = True