from pydantic import BaseModel


class NetworkBase(BaseModel):
    project: str
    hostname: str
    name: str
    cidr: str | None = None


class NetworkCreate(NetworkBase):
    class Config:
        orm_mode = True


class NetworkDelete(BaseModel):
    project: str
    cidr: str


class NetworkUpdate(BaseModel):
    network_id: str
    target_network_id: str | None = None
    ig_id: str | None = None
    route_table: str | None = None
    created: bool | None = None


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
    target_subnet_id: str | None = None
    created: bool | None = None