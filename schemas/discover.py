from utils.id_gen import unique_id_gen
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class DiscoverBase(BaseModel):
    project: str
    provider: str
    hosts: list
    username: str
    password: str


class DiscoverCreate(BaseModel):
    id: str = Field(default_factory=unique_id_gen("DS"))
    project: str = Field(alias='project_id')
    hostname: str
    network: str
    subnet: str
    ports: Optional[None] = None
    cpu_core: int
    cpu_model: str
    ram: str
    disk_details: list
    ip: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True


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
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True