from mongoengine import *
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns

class Discover(Model):
    host = columns.Text(primary_key=True, max_length=200 )
    ip = columns.Text(required=True)
    subnet = columns.Text(required=True, max_length=150)
    network = columns.Text(required=True, max_length=150)
    ports = columns.List(value_type=columns.Map(key_type=columns.Text(),value_type=columns.Text()))
    cores = columns.Text(max_length=2)
    cpu_model = columns.Text(required=True, max_length=150)
    ram = columns.Text(required=True, max_length=150)
    disk_details = columns.List(value_type=columns.Map(key_type=columns.Text(),value_type=columns.Text()))
    project = columns.Text(primary_key=True, max_length=150)
    public_ip = columns.Text(required=True, max_length=150)
    meta = {'allow_inheritance': True}


class DiscoverMongo(Document):
    host = StringField(required=True, max_length=200 )
    ip = StringField(required=True)
    subnet = StringField(required=True, max_length=150)
    network = StringField(required=True, max_length=150)
    ports = ListField()
    cores = StringField(max_length=2)
    cpu_model = StringField(required=True, max_length=150)
    ram = StringField(required=True, max_length=150)
    disk_details = ListField()
    project = StringField(required=True, max_length=150)
    public_ip = StringField(required=True, max_length=150)
    meta = {
        'indexes': [
            {'fields': ('host', 'project'), 'unique': True}
        ]
    }

