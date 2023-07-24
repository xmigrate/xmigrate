from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Union


class VMCreate(BaseModel):
    blueprint_id: str
    hostname: str
    network: Union[str, None] = None
    ports: Union[str, None] = None
    cpu_core: Union[int, None] = None
    cpu_model: Union[str, None] = None
    ram: Union[str, None] = None


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
    updated_at: datetime = Field(default_factory=datetime.now())

    class Config:
        allow_population_by_field_name = True