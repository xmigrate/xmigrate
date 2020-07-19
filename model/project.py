from mongoengine import *


class Project(Document):
    provider = StringField(required=True, max_length=20)
    location = StringField(required=True)
    name = StringField(required=True, max_length=50,unique=True)
    resource_group = StringField(max_length=100)
    subscription_id = StringField(max_length=100)