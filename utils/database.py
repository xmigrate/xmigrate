from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

username = os.getenv("DB_USER")
password = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")
db_url = os.getenv("DB_URL")

SQLALCHEMY_DATABASE_URL = f"postgresql://{username}:{password}@{db_url}/{db_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

LocalSession = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


async def dbconn():
    with LocalSession() as db:
        yield db