from utils.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String


class Storage(Base):
    
    __tablename__ = 'storage'

    id = Column(String(40), primary_key=True, unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    bucket_name = Column(String(256), primary_key=True)
    access_key = Column(String(256))
    secret_key = Column(String(256))
    container = Column(String(256))
    project = Column(String(40), ForeignKey("project.id"), primary_key=True)