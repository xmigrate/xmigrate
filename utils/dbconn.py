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
    sync_table(Disk)
    session.execute("CREATE INDEX IF NOT EXISTS ON blue_print (network);")
    session.execute("CREATE INDEX IF NOT EXISTS ON blue_print (subnet);")
    return session
