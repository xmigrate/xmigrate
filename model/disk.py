from utils.database import Base
from sqlalchemy import Column, String


class Disk(Base):
    
    __tablename__ = 'disk'
    
    project = Column(String, primary_key=True, unique=True)
    host = Column(String, primary_key=True)
    vhd = Column(String, nullable=False)
    file_size = Column(String, nullable=False)
    mnt_path = Column(String, nullable=False)
    disk_id = Column(String, nullable=False)