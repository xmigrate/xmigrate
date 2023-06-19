from pydantic import BaseModel
from typing import Union, Dict


class ProjectBase(BaseModel):
    name: str
    provider: str
    location: str
    aws_access_key: Union[str, None] = None
    aws_secret_key: Union[str, None] = None
    azure_client_id: Union[str, None] = None
    azure_client_secret: Union[str, None] = None
    azure_tenant_id: Union[str, None] = None
    azure_resource_group: Union[str, None] = None
    azure_resource_group_created: bool = False
    gcp_service_token: Union[Dict, None] = None


class ProjectUpdate(ProjectBase):
    project_id: str
    name: None =  None
    provider: None = None
    location: None = None
    class Config:
        orm_mode = True