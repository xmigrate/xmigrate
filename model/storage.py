from mongoengine import *


class Storage(Document):
    project = StringField(required=True, max_length=20,unique=True)
    storage = StringField(required=True)
    container = StringField(required=True)
    access_key = StringField(required=True, max_length=150)


class Bucket(Document):
    project = StringField(required=True, max_length=20,unique=True)
    bucket = StringField(required=True)
    secret_key = StringField(required=True, max_length=150)
    access_key = StringField(required=True, max_length=150)