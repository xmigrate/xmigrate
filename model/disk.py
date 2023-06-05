from utils.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String


class Disk(Base):
    
    __tablename__ = 'disk'

    id = Column(String(40), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    host = Column(String(256))
    vhd = Column(String(256))
    file_size = Column(String(256))
    mnt_path = Column(String(256))
    disk_clone = Column(String(256))
    blueprint = Column(String(40), ForeignKey("blueprint.id"), nullable=False)