from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Union, Dict


class ProjectBase(BaseModel):
    name: str
    provider: str
    location: str
    aws_access_key: Union[str, None] = None
    aws_secret_key: Union[str, None] = None
    azure_client_id: Union[str, None] = None
    azure_client_secret: Union[str, None] = None
    azure_tenant_id: Union[str, None] = None
    azure_subscription_id: Union[str, None] = None
    azure_resource_group: Union[str, None] = None
    azure_resource_group_created: Union[bool, None] = None
    gcp_service_token: Union[Dict, None] = None


class ProjectUpdate(BaseModel):
    id: str = Field(alias='project_id')
    provider: Optional[str] = None
    location: Optional[str] = None
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_subscription_id: Optional[str] = None
    azure_resource_group: Optional[str] = None
    azure_resource_group_created: Optional[bool] = None
    gcp_service_token: Optional[dict] = None
    updated_at: datetime = Field(default_factory=datetime.now())

    class Config:
        allow_population_by_field_name = True