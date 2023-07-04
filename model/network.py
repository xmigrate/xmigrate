from utils.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String


class Network(Base):
    
    __tablename__ = 'network'
    
    id = Column(String(40), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    blueprint = Column(String(40), ForeignKey("blueprint.id"), nullable=False)
    name = Column(String(256))
    cidr = Column(String(256))
    created = Column(Boolean, nullable=False, default=False)
    target_network_id = Column(String(256))
    ig_id = Column(String(256))
    route_table = Column(String(256))


class Subnet(Base):
    
    __tablename__ = 'subnet'

    id = Column(String(40), primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    network = Column(String(40), ForeignKey("network.id"), nullable=False)
    subnet_type = Column(String(256))
    subnet_name = Column(String(256))
    cidr = Column(String(256))
    created = Column(Boolean, nullable=False, default=False)
    target_subnet_id = Column(String(256))