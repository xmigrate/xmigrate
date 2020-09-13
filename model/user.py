from mongoengine import *

class User(Document):
    username = StringField(required=True, max_length=20,unique=True)
    password = StringField(required=True)