from utils.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String


class Blueprint(Base):
    
    __tablename__ = 'blueprint'

    id = Column(String(40), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    is_locked = Column(Boolean, nullable=False, default=False)
    is_enabled = Column(Boolean, nullable=False, default=True)
    project = Column(String(40), ForeignKey("project.id"), primary_key=True)