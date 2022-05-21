from mongoengine import *
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns

class User(Model):
    username = columns.Text(primary_key=True, max_length=20)
    password = columns.Text(required=True)
    active = columns.Boolean(default=True)

class UserMongo(Document):
    username = StringField(required=True, max_length=20,unique=True)
    password = StringField(required=True)
    active = BooleanField(default=True)