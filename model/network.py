from mongoengine import *

class Network(Document):
    cidr = StringField(required=True, max_length=50)
    project = StringField(required=True, max_length=50)
    nw_name = StringField(required=True, max_length=50)
    meta = {
        'indexes': [
            {'fields': ('cidr', 'project','nw_name'), 'unique': True}
        ]
    }

class Subnet(Document):
    cidr = StringField(required=True, max_length=50)
    nw_name = StringField(required=False, max_length=100)
    project = StringField(required=True, max_length=50)
    subnet_name = StringField(required=True, max_length=150)
    subnet_type = BooleanField(required=True)
    meta = {
        'indexes': [
            {'fields': ('cidr', 'project','subnet_name'), 'unique': True}
        ]
    }