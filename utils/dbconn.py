from mongoengine import *
from dotenv import load_dotenv
from os import getenv
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from cassandra.query import ordered_dict_factory
from model.discover import *
from model.blueprint import *
from model.disk import *
from model.storage import *
from model.project import *
from model.network import *
from model.user import *



load_dotenv()

db = getenv("MONGO_DB")
couch_db = getenv("COUCH_DB")

# def create_db_con():
#     con = connect(host=db)
#     return con

#########CouchDB#############
def create_couchdb_con():
    con = couchdb.Server(couch_db)
    return con

def couchdb_con():
    con = create_couchdb_con()
    try:
        db = con['migration']
    except couchdb.http.ResourceNotFound:
        db = con.create('migration')
    return db

##################################

cass_db = getenv("CASS_DB")
cass_password = getenv("CASS_PASSWORD")
cass_user = getenv("CASS_USER")

def create_db_con():
    auth_provider = PlainTextAuthProvider(username=cass_user, password=cass_password)
    cluster = Cluster([cass_db],auth_provider=auth_provider)
    session = cluster.connect()
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS migration
        WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
        """)
    session.set_keyspace('migration')
    session.row_factory = ordered_dict_factory
    connection.setup([cass_db], "migration",protocol_version=3,auth_provider=auth_provider)
    sync_table(BluePrint)
    sync_table(Discover)
    sync_table(Project)
    sync_table(Network)
    sync_table(Subnet)
    sync_table(Storage)
    sync_table(Bucket)
    sync_table(GcpBucket)
    sync_table(User)
    session.execute("CREATE INDEX IF NOT EXISTS ON blue_print (network);")
    session.execute("CREATE INDEX IF NOT EXISTS ON blue_print (subnet);")
    return session


# from cassandra.cqlengine import columns
# from cassandra.cqlengine import connection
# from datetime import datetime
# from cassandra.cqlengine.management import sync_table
# from cassandra.cqlengine.models import Model

# #first, define a model
# class ExampleModel(Model):
#     project      = columns.Text(primary_key=True)
#     example_type    = columns.Integer(index=True)
#     created_at      = columns.DateTime()
#     hostname     = columns.Text(primary_key=True)