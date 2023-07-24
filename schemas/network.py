from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Union


class NetworkBase(BaseModel):
    project: str
    hosts: list
    name: str
    cidr: Union[str, None] = None


class NetworkCreate(NetworkBase):
    class Config:
        orm_mode = True


class NetworkDelete(BaseModel):
    project: str
    name: str


class NetworkUpdate(BaseModel):
    id: str = Field(alias='network_id')
    target_network_id: Optional[str] = None
    ig_id: Optional[str] = None
    route_table: Optional[str] = None
    created: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.now())

    class Config:
        allow_population_by_field_name = True


class SubnetCreate(BaseModel):
    project: str
    nw_cidr: str
    cidr: str
    name: str
    nw_type: str


class SubnetDelete(NetworkDelete):
    subnet_name: str
    
    class Config:
        orm_mode = True

        
class SubnetUpdate(BaseModel):
    id: str = Field(alias='subnet_id')
    target_subnet_id: Optional[str] = None
    created: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.now())

    class Config:
        allow_population_by_field_name = True