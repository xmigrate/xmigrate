from utils.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String


class Discover(Base):
    
    __tablename__ = 'discover'

    id = Column(String(40), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    is_locked = Column(Boolean, nullable=False, default=False)
    is_enabled = Column(Boolean, nullable=False, default=True)
    project = Column(String(40), ForeignKey("project.id"), nullable=False)
    hostname = Column(String(256))
    network = Column(String(256))
    subnet = Column(String(256))
    ports = Column(String(256))
    cpu_core = Column(Integer)
    cpu_model = Column(String(256))
    ram = Column(String(256))
    disk_details = Column(String(5120))
    ip = Column(String(256))