from mongoengine import *
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns

class Network(Model):
    cidr = columns.Text(primary_key=True, max_length=50)
    project = columns.Text(primary_key=True, max_length=50)
    nw_name = columns.Text(primary_key=True, max_length=50)
    created = columns.Boolean(required=True, default=False)


class NetworkMongo(Document):
    cidr = StringField(required=True, max_length=50)
    project = StringField(required=True, max_length=50)
    nw_name = StringField(required=True, max_length=50)
    created = BooleanField(required=True, default=False)
    meta = {
        'indexes': [
            {'fields': ('cidr', 'project','nw_name'), 'unique': True}
        ]
    }


class Subnet(Model):
    cidr = columns.Text(primary_key=True, max_length=50)
    nw_name = columns.Text(required=False, max_length=100)
    project = columns.Text(primary_key=True, max_length=50)
    subnet_name = columns.Text(primary_key=True, max_length=150)
    subnet_type = columns.Boolean(required=True)
    created = columns.Boolean(required=True, default=False)


class SubnetMongo(Document):
    cidr = StringField(required=True, max_length=50)
    nw_name = StringField(required=False, max_length=100)
    project = StringField(required=True, max_length=50)
    subnet_name = StringField(required=True, max_length=150)
    subnet_type = BooleanField(required=True)
    created = BooleanField(required=True, default=False)
    meta = {
        'indexes': [
            {'fields': ('cidr', 'project','subnet_name'), 'unique': True}
        ]
    }