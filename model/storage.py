from mongoengine import *


class Storage(Document):
    project = StringField(required=True, max_length=20,unique=True)
    storage = StringField(required=True)
    accesskey = StringField(required=True, max_length=150)