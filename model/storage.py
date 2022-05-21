from mongoengine import *
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns

class Storage(Model):
    project = columns.Text(primary_key=True, max_length=20)
    storage = columns.Text(primary_key=True)
    container = columns.Text(required=True)
    access_key = columns.Text(required=True, max_length=150)

class StorageMongo(Document):
    project = StringField(required=True, max_length=20)
    storage = StringField(required=True)
    container = StringField(required=True)
    access_key = StringField(required=True, max_length=150)
    meta = {
        'indexes': [
            {'fields': ('storage', 'project'), 'unique': True}
        ]
    }

class Bucket(Model):
    project = columns.Text(primary_key=True, max_length=20)
    bucket = columns.Text(primary_key=True)
    secret_key = columns.Text(required=True, max_length=150)
    access_key = columns.Text(required=True, max_length=150)


class BucketMongo(Document):
    project = StringField(required=True, max_length=20)
    bucket = StringField(required=True)
    secret_key = StringField(required=True, max_length=150)
    access_key = StringField(required=True, max_length=150)
    meta = {
        'indexes': [
            {'fields': ('bucket', 'project'), 'unique': True}
        ]
    }


class GcpBucket(Model):
    project = columns.Text(primary_key=True, max_length=20)
    project_id= columns.Text(required=True, max_length=150)
    secret_key = columns.Text(required=True, max_length=150)
    access_key = columns.Text(required=True, max_length=150)
    bucket = columns.Text(primary_key=True)


class GcpBucketMongo(Document):
    project = StringField(required=True, max_length=20)
    project_id= StringField(required=True, max_length=150)
    secret_key = StringField(required=True, max_length=150)
    access_key = StringField(required=True, max_length=150)
    bucket = StringField(required=True)
    meta = {
        'indexes': [
            {'fields': ('bucket', 'project'), 'unique': True}
        ]
    }
