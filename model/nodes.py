from utils.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String


class Nodes(Base):
    
    __tablename__ = 'node'

    id = Column(String(40), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    hosts = Column(String(5120), nullable=False)
    username = Column(String(256), nullable=False)
    password = Column(String(256), nullable=False)
    project = Column(String(40), ForeignKey("project.id"), nullable=False)