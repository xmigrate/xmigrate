from utils.id_gen import unique_id_gen
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class NetworkCreate(BaseModel):
    id: str = Field(default_factory=unique_id_gen)
    blueprint: Optional[str] = Field(alias='blueprint_id')
    project: str
    hosts: list
    name: str
    cidr: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True


class NetworkDelete(BaseModel):
    project: str
    name: str


class NetworkUpdate(BaseModel):
    id: str = Field(alias='network_id')
    target_network_id: Optional[str] = None
    ig_id: Optional[str] = None
    route_table: Optional[str] = None
    created: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True


class SubnetCreate(BaseModel):
    id: str = Field(default_factory=unique_id_gen)
    network: Optional[str] = Field(alias='network_id')
    project: str
    nw_cidr: str
    cidr: str
    subnet_name: str = Field(alias='name')
    subnet_type: str = Field(alias='nw_type')
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True


class SubnetDelete(NetworkDelete):
    subnet_name: str
    
    class Config:
        orm_mode = True

        
class SubnetUpdate(BaseModel):
    id: str = Field(alias='subnet_id')
    target_subnet_id: Optional[str] = None
    created: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True