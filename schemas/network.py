from pydantic import BaseModel
from typing import Union


class NetworkBase(BaseModel):
    project: str
    name: str
    cidr: Union[str, None] = None


class NetworkCreate(NetworkBase):
    class Config:
        orm_mode = True


class NetworkDelete(BaseModel):
    project: str
    cidr: str


class NetworkUpdate(BaseModel):
    network_id: str
    target_network_id: Union[str, None] = None
    ig_id: Union[str, None] = None
    route_table: Union[str, None] = None
    created: bool = False


class SubnetCreate(BaseModel):
    project: str
    nw_cidr: str
    cidr: str
    name: str
    nw_type: str


class SubnetDelete(NetworkDelete):
    subnet_cidr: str
    
    class Config:
        orm_mode = True

        
class SubnetUpdate(BaseModel):
    subnet_id: str
    target_subnet_id: Union[str, None] = None
    created: bool = False