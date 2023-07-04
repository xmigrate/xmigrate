from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str
    provider: str
    location: str
    aws_access_key: str | None = None
    aws_secret_key: str | None = None
    azure_client_id: str | None = None
    azure_client_secret: str | None = None
    azure_tenant_id: str | None = None
    azure_subscription_id: str | None = None
    azure_resource_group: str | None = None
    azure_resource_group_created: bool | None = None
    gcp_service_token: dict | None = None


class ProjectUpdate(ProjectBase):
    project_id: str
    name: str | None = None
    provider: str | None = None
    location: str | None = None
    class Config:
        orm_mode = True