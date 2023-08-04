from utils.constants import Provider
from utils.database import Base
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, String
  
    
class Project(Base):
    
    __tablename__ = "project"

    id = Column(String(40), primary_key=True, unique=True)
    name = Column(String(256), primary_key=True)
    provider = Column(String(256), nullable=False)
    location = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    is_locked = Column(Boolean, nullable=False, default=False)
    is_enabled = Column(Boolean, nullable=False, default=True)
    aws_access_key = Column(String(256))
    aws_secret_key = Column(String(256))
    azure_client_id	= Column(String(256))
    azure_client_secret	= Column(String(256))
    azure_tenant_id	= Column(String(256))
    azure_subscription_id = Column(String(256))
    azure_resource_group = Column(String(256))
    azure_resource_group_created = Column(Boolean, default=False)
    gcp_service_token = Column(String(5120))

    __table_args__ = (CheckConstraint(
        provider.in_([e.value for e in Provider]), name='enforce_providers')
    ,) # Trailing comma necessary for assigning type tuple