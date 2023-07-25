from utils.id_gen import unique_id_gen
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class VMCreate(BaseModel):
    id: str = Field(default_factory=unique_id_gen)
    blueprint: str = Field(alias='blueprint_id')
    hostname: str
    network: Optional[str] = None
    ports: Optional[str] = None
    cpu_core: Optional[int] = None
    cpu_model: Optional[str] = None
    ram: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True


class VMUpdate(BaseModel):
    id: str = Field(alias='machine_id')
    network: Optional[str] = None
    ports: Optional[str] = None
    cpu_core: Optional[int] = None
    cpu_model: Optional[str] = None
    ram: Optional[str] = None
    ip: Optional[str] = None
    ip_created: Optional[bool] = None
    machine_type: Optional[str] = None
    public_route: Optional[bool] = None
    status: Optional[str] = None
    image_id: Optional[str] = None
    vm_id: Optional[str] = None
    nic_id: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True