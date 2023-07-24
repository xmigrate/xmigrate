from pydantic import BaseModel
from typing import Optional


class LocationBase(BaseModel):
    provider: str
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_subscription_id: Optional[str] = None
    gcp_service_token: Optional[dict] = None