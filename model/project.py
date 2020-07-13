from mongoengine import *


class Project(Document):
    provider = StringField(required=True, max_length=20)
    location = StringField(required=True)
    name = StringField(required=True, max_length=50)
