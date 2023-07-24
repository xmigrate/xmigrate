from utils.id_gen import unique_id_gen
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class ProjectCreate(BaseModel):
    id: str = Field(default=unique_id_gen("PJ"))
    name: str
    provider: str
    location: str
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_subscription_id: Optional[str] = None
    azure_resource_group: Optional[str] = None
    azure_resource_group_created: Optional[bool] = None
    gcp_service_token: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


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
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True