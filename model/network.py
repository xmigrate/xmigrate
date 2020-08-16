from mongoengine import *

class Network(Document):
    cidr = StringField(required=True, max_length=50,unique=True)
    nw_id = StringField(required=False, max_length=100, unique=True)
    project = StringField(required=True, max_length=50)
    nw_name = StringField(required=True, max_length=50,unique=True)


class Subnet(Document):
    cidr = StringField(required=True, max_length=50,unique=True)
    nw_name = StringField(required=False, max_length=100)
    project = StringField(required=True, max_length=50)
    subnet_name = StringField(required=True, max_length=150,unique=True)
    subnet_id = StringField(required=True, max_length=250,unique=True)
    subnet_type = StringField(required=True, max_length=10)
