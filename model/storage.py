from utils.dbconn import Base
from sqlalchemy import Column, String


class Storage(Base):
    
    __tablename__ = 'storage'

    project = Column(String, primary_key=True)
    storage = Column(String, unique=True, nullable=False)
    container = Column(String, nullable=False)
    access_key = Column(String, nullable=False)
   

class Bucket(Base):

    __tablename__ = 'bucket'

    project = Column(String, primary_key=True)
    bucket = Column(String, unique=True, nullable=False)
    secret_key = Column(String, nullable=False)
    access_key = Column(String, nullable=False)


class GcpBucket(Base):
    
    __tablename__ = 'gcp_bucket'

    project = Column(String, primary_key=True)
    project_id= Column(String, nullable=False)
    bucket = Column(String, unique=True, nullable=False)
    secret_key = Column(String, nullable=False)
    access_key = Column(String, nullable=False)