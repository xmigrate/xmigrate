from pydantic import BaseModel
from typing import Dict, Union


class LocationBase(BaseModel):
    provider: str
    aws_access_key: Union[str, None] = None
    aws_secret_key: Union[str, None] = None
    azure_client_id: Union[str, None] = None
    azure_client_secret: Union[str, None] = None
    azure_tenant_id: Union[str, None] = None
    azure_subscription_id: Union[str, None] = None
    gcp_service_token: Union[Dict, None] = None