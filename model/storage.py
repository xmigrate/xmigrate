from mongoengine import *


class Storage(Document):
    project = StringField(required=True, max_length=20)
    storage = StringField(required=True)
    container = StringField(required=True)
    access_key = StringField(required=True, max_length=150)
    meta = {
        'indexes': [
            {'fields': ('storage', 'project'), 'unique': True}
        ]
    }


class Bucket(Document):
    project = StringField(required=True, max_length=20)
    bucket = StringField(required=True)
    secret_key = StringField(required=True, max_length=150)
    access_key = StringField(required=True, max_length=150)
    meta = {
        'indexes': [
            {'fields': ('bucket', 'project'), 'unique': True}
        ]
    }


class GcpBucket(Document):
    project = StringField(required=True, max_length=20)
    bucket = StringField(required=True)
    service_account = StringField(required=True)
    meta = {
        'indexes': [
            {'fields': ('bucket', 'project'), 'unique': True}
        ]
    }
