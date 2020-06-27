from mongoengine import *
from dotenv import load_dotenv
from os import getenv
load_dotenv()

db = getenv("MONGO_DB")
def create_db_con():
    con = connect(host=db)
    return con
