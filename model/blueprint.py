from utils.database import Base
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, JSON


class Blueprint(Base):
    
    __tablename__ = 'blueprint'
    
    project = Column(String, ForeignKey("project.name", onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, unique=True)
    host = Column(String, primary_key=True)
    ip = Column(String, nullable=False)
    ip_created = Column(Boolean, nullable=False, default=False)
    subnet = Column(String, nullable=False)
    network = Column(String, nullable=False)
    ports = Column(ARRAY(String))
    cores = Column(String)
    cpu_model = Column(String, nullable=False)
    ram = Column(String, nullable=False)
    machine_type = Column(String, nullable=False)
    status = Column(String)
    image_id = Column(String)
    vpc_id = Column(String)
    subnet_id = Column(String)
    public_route = Column(Boolean)
    ig_id = Column(String)
    route_table = Column(String)
    vm_id = Column(String)
    nic_id = Column(String)
    disk_clone = Column(ARRAY(JSON(String)))