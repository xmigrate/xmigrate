from utils.database import Base
from sqlalchemy import Column, String, Boolean


class User(Base):
    
    __tablename__ = 'user'

    username = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)