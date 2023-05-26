from utils.database import Base
from sqlalchemy import Column, String, ForeignKey


class Storage(Base):
    
    __tablename__ = 'storage'

    project = Column(String, ForeignKey("project.name", onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, unique=True)
    storage = Column(String, primary_key=True)
    container = Column(String, nullable=False)
    access_key = Column(String, nullable=False)
   

class Bucket(Base):

    __tablename__ = 'bucket'

    project = Column(String, ForeignKey("project.name", onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, unique=True)
    bucket = Column(String, primary_key=True)
    secret_key = Column(String, nullable=False)
    access_key = Column(String, nullable=False)


class GcpBucket(Base):
    
    __tablename__ = 'gcp_bucket'

    project = Column(String, ForeignKey("project.name", onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, unique=True)
    project_id= Column(String, nullable=False)
    bucket = Column(String, primary_key=True)
    secret_key = Column(String, nullable=False)
    access_key = Column(String, nullable=False)