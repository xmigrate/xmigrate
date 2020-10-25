from mongoengine import *

class Network(Document):
    cidr = StringField(required=True, max_length=50)
    project = StringField(required=True, max_length=50)
    nw_name = StringField(required=True, max_length=50,unique=True)


class Subnet(Document):
    cidr = StringField(required=True, max_length=50)
    nw_name = StringField(required=False, max_length=100)
    project = StringField(required=True, max_length=50)
    subnet_name = StringField(required=True, max_length=150,unique=True)
    subnet_type = StringField(required=True, max_length=10)
