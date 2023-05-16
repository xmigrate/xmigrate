from utils.dbconn import Base
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import ARRAY, JSON


class Project(Base):
    
    __tablename__ = "project"

    name = Column(String, primary_key=True, unique=True)
    provider = Column(String, nullable=False)
    location = Column(String, nullable=False)
    resource_group = Column(String)
    subscription_id = Column(String)
    client_id = Column(String)
    secret = Column(String)
    tenant_id = Column(String)
    users = Column(ARRAY(String), nullable=False)
    access_key = Column(String)
    secret_key = Column(String)
    resource_group_created = Column(Boolean, nullable=False, default=False)
    username = Column(String)
    password = Column(String)
    public_ip = Column(ARRAY(String))
    service_account = Column(JSON(String))
    gcp_project_id = Column(String)