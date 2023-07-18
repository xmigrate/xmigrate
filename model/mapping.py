from utils.database import Base
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String

class Mapper(Base):
    
    __tablename__ = 'mapper'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    is_enabled = Column(Boolean, nullable=False, default=True)
    project = Column(String(40), ForeignKey("project.id"), nullable=False)
    user = Column(String(40), ForeignKey("user.id"), nullable=False)
    user_role = Column(String(1024))