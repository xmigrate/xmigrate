from utils.dbconn import Base
from sqlalchemy import Column, String


class Network(Base):
    
    __tablename__ = 'network'
    
    project = Column(String, primary_key=True, unique=True)
    nw_name = Column(String, primary_key=True)
    cidr = Column(String, primary_key=True)
    created = Column(String, nullable=False, default=False)


class Subnet(Base):
    
    __tablename__ = 'subnet'
    
    project = Column(String, primary_key=True, unique=True)
    nw_name = Column(String, primary_key=True)
    subnet_name = Column(String, primary_key=True)
    subnet_type = Column(String, nullable=False)
    cidr = Column(String, primary_key=True)
    created = Column(String, nullable=False, default=False)