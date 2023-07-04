from pydantic import BaseModel


class LocationBase(BaseModel):
    provider: str
    aws_access_key: str | None = None
    aws_secret_key: str | None = None
    azure_client_id: str | None = None
    azure_client_secret: str | None = None
    azure_tenant_id: str | None = None
    azure_subscription_id: str | None = None
    gcp_service_token: dict | None = None