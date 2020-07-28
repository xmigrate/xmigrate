from mongoengine import *


class Disk(Document):
    host = StringField(required=True, max_length=150)
    vhd = StringField(required=True)
    file_size = StringField(required=True)
    project = StringField(required=True, max_length=50,unique=True)
