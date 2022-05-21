from mongoengine import *
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns

class Disk(Model):
    host = columns.Text(primary_key=True, max_length=150)
    vhd = columns.Text(required=True)
    file_size = columns.Text(required=True)
    project = columns.Text(primary_key=True, max_length=150)
    mnt_path = columns.Text(primary_key=True, max_length=150)
    disk_id = columns.Text(required=True, max_length=550)


class DiskMongo(Document):
    host = StringField(required=True, max_length=150)
    vhd = StringField(required=True)
    file_size = StringField(required=True)
    project = StringField(required=True, max_length=150)
    mnt_path = StringField(required=True, max_length=150)
    disk_id = StringField(required=True, max_length=550)
    meta = {
        'indexes': [
            {'fields': ('host', 'project', 'mnt_path'), 'unique': True}
        ]
    }