from utils.database import Base
from sqlalchemy import Column, String, Boolean, ForeignKey


class Network(Base):
    
    __tablename__ = 'network'
    
    project = Column(String, ForeignKey("project.name", onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, unique=True)
    nw_name = Column(String, primary_key=True, unique=True)
    cidr = Column(String, primary_key=True)
    created = Column(Boolean, nullable=False, default=False)


class Subnet(Base):
    
    __tablename__ = 'subnet'
    
    project = Column(String, ForeignKey("project.name", onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, unique=True)
    nw_name = Column(String, ForeignKey("network.nw_name", onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    subnet_name = Column(String, primary_key=True)
    subnet_type = Column(String, nullable=False)
    cidr = Column(String, primary_key=True)
    created = Column(Boolean, nullable=False, default=False)