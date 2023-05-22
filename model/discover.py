from utils.database import Base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY, JSON


class Discover(Base):
    
    __tablename__ = 'discover'
    
    project = Column(String, primary_key=True, unique=True)
    host = Column(String, primary_key=True)
    ip = Column(String, nullable=False)
    subnet = Column(String, nullable=False)
    network = Column(String, nullable=False)
    ports = Column(ARRAY(String))
    cores = Column(String)
    cpu_model = Column(String, nullable=False)
    ram = Column(String, nullable=False)
    disk_details = Column(ARRAY(JSON(String)))
    public_ip = Column(String, nullable=False)