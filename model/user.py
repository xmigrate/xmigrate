from utils.database import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String


class User(Base):
    
    __tablename__ = 'user'

    id = Column(String(40), primary_key=True, unique=True)
    username = Column(String(256), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    is_locked = Column(Boolean, nullable=False, default=False)
    is_enabled = Column(Boolean, nullable=False, default=True)
    wrong_pass_count = Column(Integer, nullable=False, default=0)
    is_cred_expired = Column(Integer, nullable=False, default=0)