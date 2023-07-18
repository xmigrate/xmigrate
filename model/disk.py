from utils.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String


class Disk(Base):
    
    __tablename__ = 'disk'

    id = Column(String(40), primary_key=True, unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    hostname = Column(String(256))
    vhd = Column(String(256))
    file_size = Column(String(256))
    mnt_path = Column(String(256), primary_key=True)
    disk_clone = Column(String(256))
    target_disk_id = Column(String(256))
    vm = Column(String(40), ForeignKey("vm.id"), primary_key=True)