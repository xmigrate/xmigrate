from mongoengine import *
from dotenv import load_dotenv
from os import getenv
import couchdb

load_dotenv()

db = getenv("MONGO_DB")
couch_db = getenv("COUCH_DB")

def create_db_con():
    con = connect(host=db)
    return con

def create_couchdb_con():
    con = couchdb.Server(couch_db)
    return con