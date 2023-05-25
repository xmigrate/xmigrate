from utils.database import Base
from sqlalchemy import Column, String, Boolean


class Network(Base):
    
    __tablename__ = 'network'
    
    project = Column(String, primary_key=True, unique=True)
    nw_name = Column(String, nullable=False)
    cidr = Column(String, primary_key=True)
    created = Column(Boolean, nullable=False, default=False)


class Subnet(Base):
    
    __tablename__ = 'subnet'
    
    project = Column(String, primary_key=True, unique=True)
    nw_name = Column(String, primary_key=True)
    subnet_name = Column(String, nullable=False)
    subnet_type = Column(String, nullable=False)
    cidr = Column(String, primary_key=True)
    created = Column(Boolean, nullable=False, default=False)